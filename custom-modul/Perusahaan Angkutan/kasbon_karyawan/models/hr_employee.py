from odoo import api, fields, models

class HREmployeeKasbonKaryawan(models.Model):
    _inherit = 'hr.employee'

    hutang_karyawan = fields.Float(digits=(6,0), readonly=True)
