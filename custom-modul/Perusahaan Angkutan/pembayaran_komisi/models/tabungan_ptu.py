from odoo import api, models, fields

class TabunganPTU(models.Model):
    _name = 'tabungan.ptu'
    _description = 'Tabungan PTU'
    _rec_name = 'kode'

    kode = fields.Char(string="Kode")
    tanggal = fields.Datetime(string="Tanggal", default=fields.Datetime.now())
    karyawan = fields.Many2one('hr.employee', string="Karyawan")
    saldo = fields.Float(string="Saldo", compute="compute_saldo_tabungan")
    nominal_ptu = fields.Float(string="Nominal PTU")

    @api.depends('karyawan')
    def compute_saldo_tabungan(self):
        for record in self:
            if record.karyawan:
                tabungan = self.env['hr.employee.ptu_line'].search([('employee_id', '=', record.karyawan.id)])
                record.saldo = sum(tabungan.mapped('nominal'))
            else:
                record.saldo = 0.0