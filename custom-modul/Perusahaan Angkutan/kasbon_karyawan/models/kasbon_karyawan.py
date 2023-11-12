from odoo import api, models, fields

class KasbonKaryawan(models.Model):
    _name = 'kasbon.karyawan'
    _description = 'Kasbon Karyawan'
    _inherit = ['mail.thread']

    tipe_kasbon = fields.Selection([
        ('pinjam', 'Pinjam'),
        ('bayar', 'Bayar')],
        string='Tipe Kasbon', default='pinjam', required=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('paid', "Paid"),
    ], default='draft', string="State", index=True, hide=True, tracking=True)




    active = fields.Boolean('Archive', default=True, tracking=True)
    nama_karyawan = fields.Many2one('res.partner', 'Nama Karyawan')
    rekening_karyawan = fields.Many2one('res.partner.bank', 'Rekening')
    sisa_piutang = fields.Float('Sisa Piutang', compute='_compute_sisa_hutang', digits=(6, 0))
    nominal_pinjam = fields.Float('Nominal Pinjam', digits=(6, 0))
    nominal_bayar = fields.Float('Nominal Bayar', digits=(6, 0))
    keterangan = fields.Text('Keterangan')
    akun_piutang = fields.Many2one('account.account')
    akun_kas = fields.Many2one('account.journal')

    @api.onchange('nama_karyawan')
    def onchange_nama_karyawan(self):
        if self.nama_karyawan:
            return {'domain': {'rekening_karyawan': [('partner_id', '=', self.nama_karyawan.id)]}}
        else:
            return {'domain': {'rekening_karyawan': []}}

    history_hutang = fields.One2many('history.hutang', inverse_name='kasbon_karyawan', states={
        'draft': [('readonly', False)],
        'paid': [('readonly', True)],
    })

    history_bayar = fields.One2many('history.bayar', inverse_name='kasbon_karyawan', states={
        'draft': [('readonly', False)],
        'paid': [('readonly', True)],
    })

    @api.depends('history_hutang', 'history_bayar')
    def _compute_sisa_hutang(self):
        for record in self:
            nominal_hutang = sum(record.history_hutang.mapped('nominal_hutang'))
            nominal_bayar = sum(record.history_bayar.mapped('nominal_bayar'))

            record.sisa_piutang = nominal_hutang - nominal_bayar



class HistoryHutang(models.Model):
    _name = 'history.hutang'
    _description = 'History Hutang'

    kasbon_karyawan = fields.Many2one('kasbon.karyawan', invisible=True)
    kode_nomor_hutang = fields.Char('No.')
    tanggal_hutang = fields.Date('Tanggal')
    nominal_hutang = fields.Float('Nominal', digits=(6, 0))

class HistoryBayar(models.Model):
    _name = 'history.bayar'
    _description = 'History Bayar'

    kasbon_karyawan = fields.Many2one('kasbon.karyawan', invisible=True)
    kode_nomor_bayar = fields.Char('No.')
    tanggal_bayar = fields.Date('Tanggal')
    nominal_bayar = fields.Float('Nominal', digits=(6, 0))




