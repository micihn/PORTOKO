from odoo import fields, models, api

class KonfigurasiTipeMuatan(models.Model):
    _name = 'konfigurasi.tipe.muatan'
    _description = 'Konfigurasi Tipe Muatan'
    _rec_name = 'tipe_muatan'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    tipe_muatan = fields.Char('Tipe Muatan')
