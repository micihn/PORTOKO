from odoo import api, models, fields

class TabunganPTU(models.Model):
    _name = 'tabungan.ptu'
    _description = 'Tabungan PTU'
    _rec_name = 'kode'

    kode = fields.Char(string="Kode")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    tanggal = fields.Datetime(string="Tanggal", default=fields.Datetime.now())
    karyawan = fields.Many2one('hr.employee', string="Karyawan")
    saldo = fields.Float(string="Saldo", compute="compute_saldo_tabungan")
    nominal_ptu = fields.Float(string="Nominal PTU")

    state = fields.Selection([
        ('draft', "Draft"),
        ('paid', "Paid"),
    ], default='draft', string="State")

    @api.depends('karyawan')
    def compute_saldo_tabungan(self):
        for record in self:
            if record.karyawan:
                tabungan = self.env['hr.employee.ptu_line'].search([('employee_id', '=', record.karyawan.id)])
                record.saldo = sum(tabungan.mapped('nominal'))
            else:
                record.saldo = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        records = super(TabunganPTU, self).create(vals_list)
        for record in records:
            record.kode = self.env['ir.sequence'].next_by_code('tabungan.ptu.sequence') or 'New'
        return records

    def create_ptu(self):
        self.env['hr.employee.ptu_line'].create({
            'employee_id': self.karyawan.id,
            'tipe': 'pemasukan',
            'nominal': self.nominal_ptu,
            'state': 'diproses',
        })

        self.state = 'paid'
