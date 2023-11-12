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
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
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
            nominal_pinjam = sum(record.history_hutang.mapped('nominal_pinjam'))
            nominal_bayar = sum(record.history_bayar.mapped('nominal_bayar'))

            record.sisa_piutang = nominal_pinjam - nominal_bayar

    def proses(self):
        if self.tipe_kasbon == 'pinjam':
            self.env['history.hutang'].create({
                "kasbon_karyawan": self.id,
                "company_id": self.env.company.id,
                "tanggal_hutang": fields.Datetime.now(),
                "nominal_pinjam": self.nominal_pinjam,
            })

            self.tipe_kasbon = 'pinjam'
            self.nominal_pinjam = 0

        elif self.tipe_kasbon == 'bayar':
            self.env['history.bayar'].create({
                "kasbon_karyawan": self.id,
                "company_id": self.env.company.id,
                "tanggal_bayar": fields.Datetime.now(),
                "nominal_bayar": self.nominal_bayar,
            })

            self.tipe_kasbon = 'pinjam'
            self.nominal_bayar = 0

class HistoryHutang(models.Model):
    _name = 'history.hutang'
    _description = 'History Hutang'

    kasbon_karyawan = fields.Many2one('kasbon.karyawan', invisible=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    kode_nomor_hutang = fields.Char('No.')
    tanggal_hutang = fields.Date('Tanggal')
    nominal_pinjam = fields.Float('Nominal', digits=(6, 0))

class HistoryBayar(models.Model):
    _name = 'history.bayar'
    _description = 'History Bayar'

    kasbon_karyawan = fields.Many2one('kasbon.karyawan', invisible=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    kode_nomor_bayar = fields.Char('No.')
    tanggal_bayar = fields.Date('Tanggal')
    nominal_bayar = fields.Float('Nominal', digits=(6, 0))




