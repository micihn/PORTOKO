from odoo import api, models, fields

class KasbonKaryawan(models.Model):
    _name = 'kasbon.karyawan'
    _description = 'Kasbon Karyawan'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(readonly=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('lended', "Lended"),
        ('returned', "Returned"),
    ], default='draft', string="State", index=True, hide=True, tracking=True)

    active = fields.Boolean('Archive', default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    nama_karyawan = fields.Many2one('res.partner', 'Nama Karyawan')
    rekening_karyawan = fields.Many2one('res.partner.bank', 'Rekening')
    nominal_pinjam = fields.Float('Nominal Pinjam', digits=(6, 0))
    nominal_sisa = fields.Float('Sisa Hutang', digits=(6, 0), readonly=True)
    tanggal = fields.Date('Tanggal')
    keterangan = fields.Text('Keterangan')
    akun_piutang = fields.Many2one('account.account')
    akun_kas = fields.Many2one('account.journal')
    journal_entry_hutang = fields.Many2many('account.move', string='Journal Entry Hutang', readonly=True, relation='kasbon_karyawan_journal_entry_hutang_rel')
    journal_entry_pelunasan_hutang = fields.Many2many('account.move', string='Journal Entry Pelunasan', readonly=True, relation='kasbon_karyawan_journal_entry_pelunasan_hutang_rel')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('kasbon.karyawan.sequence') or 'New'
        result = super(KasbonKaryawan, self).create(vals)
        return result

    @api.onchange('nama_karyawan')
    def onchange_nama_karyawan(self):
        if self.nama_karyawan:
            return {'domain': {'rekening_karyawan': [('partner_id', '=', self.nama_karyawan.id)]}}
        else:
            return {'domain': {'rekening_karyawan': []}}

    def proses_hutang(self):
        journal_entry_hutang = self.env['account.move'].sudo().create({
            'company_id': self.company_id.id,
            'move_type': 'entry',
            'date': self.tanggal,
            'ref': str(self.name) + str(" - Hutang Karyawan " + self.nama_karyawan.name),
            'line_ids': [
                (0, 0, {
                    'name': self.name,
                    'date': self.tanggal,
                    'account_id': self.akun_piutang.id,
                    'company_id': self.company_id.id,
                    'debit': self.nominal_pinjam,
                }),

                (0, 0, {
                    'name': self.name,
                    'date': self.tanggal,
                    'account_id': self.akun_kas.default_account_id.id,
                    'company_id': self.company_id.id,
                    'credit': self.nominal_pinjam,
                }),
            ],
        })
        journal_entry_hutang.action_post()

        self.journal_entry_hutang = [(6, 0, [journal_entry_hutang.id])]

        # journal_entry_hutang_list = []
        # for rec in self.journal_entry_hutang:
        #     journal_entry_hutang_list.append((6, 0, [rec.id]))

        self.nominal_sisa = self.nominal_pinjam

        self.state = 'lended'

    def wizard_pengembalian_hutang(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pelunasan.kasbon.karyawan',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('kasbon_karyawan.pelunasan_kasbon_karyawan_wizard_view').id,
        }






