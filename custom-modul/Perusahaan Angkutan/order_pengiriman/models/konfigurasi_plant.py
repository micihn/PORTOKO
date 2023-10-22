from odoo import api, fields, models

class Plant(models.Model):
    _name = 'konfigurasi.plant'
    _description = 'Plant'
    _rec_name = 'plant'

    plant = fields.Char('Plant',ondelete='restrict')