from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PelunasanKasbonKaryawan(models.TransientModel):
    _name = 'pelunasan.kasbon.karyawan'
    _description = 'Pelunasan Kasbon Karyawan'

    jurnal_kas_pengembalian = fields.Many2one('account.journal', 'Jurnal')
    jumlah_pengembalian = fields.Float('Jumlah', digits=(6, 0))
    tanggal_pengembalian = fields.Date('Tanggal')
    memo = fields.Char('Memo')

    def proses_pengembalian(self):
        for kasbon_karyawan in self.env['kasbon.karyawan'].browse(self._context.get('active_ids', [])):

            if self.jumlah_pengembalian > kasbon_karyawan.nominal_sisa:
                raise ValidationError("Nominal Pengembalian lebih besar dari Sisa Pinjaman!")

            journal_entry_pelunasan_hutang = self.env['account.move'].sudo().create({
                'company_id': kasbon_karyawan.company_id.id,
                'move_type': 'entry',
                'date': self.tanggal_pengembalian,
                'ref': str(kasbon_karyawan.name) + str(" - Pelunasan Hutang Karyawan " + kasbon_karyawan.nama_karyawan.name),
                'line_ids': [
                    (0, 0, {
                        'name': kasbon_karyawan.name,
                        'date': self.tanggal_pengembalian,
                        'account_id': self.jurnal_kas_pengembalian.default_account_id.id,
                        'company_id': kasbon_karyawan.company_id.id,
                        'debit': self.jumlah_pengembalian,
                    }),

                    (0, 0, {
                        'name': kasbon_karyawan.name,
                        'date': self.tanggal_pengembalian,
                        'account_id': kasbon_karyawan.akun_piutang.id,
                        'company_id': kasbon_karyawan.company_id.id,
                        'credit': self.jumlah_pengembalian,
                    }),
                ],
            })
            journal_entry_pelunasan_hutang.action_post()

            journal_entry_pelunasan_hutang_list = []
            for rec in kasbon_karyawan.journal_entry_pelunasan_hutang:
                journal_entry_pelunasan_hutang_list.append((6, 0, [rec.id]))

            kasbon_karyawan.journal_entry_pelunasan_hutang = journal_entry_pelunasan_hutang_list + [(4, journal_entry_pelunasan_hutang.id, 0)]

            kasbon_karyawan.nominal_sisa = kasbon_karyawan.nominal_sisa - self.jumlah_pengembalian

            kasbon_karyawan.nama_karyawan.hutang_karyawan = kasbon_karyawan.nama_karyawan.hutang_karyawan - self.jumlah_pengembalian

            if kasbon_karyawan.nominal_sisa == 0:
                kasbon_karyawan.state = 'returned'
            else:
                pass