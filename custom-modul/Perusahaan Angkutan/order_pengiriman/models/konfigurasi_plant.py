from odoo import api, fields, models

class Plant(models.Model):
    _name = 'konfigurasi.plant'
    _description = 'Plant'
    _rec_name = 'plant'

    plant = fields.Char('Plant',ondelete='restrict')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)