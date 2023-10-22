from odoo import fields, models, api

class KonfigurasiKota(models.Model):

    _name = 'konfigurasi.lokasi'
    _description = 'Konfigurasi Lokasi'
    _rec_name = 'lokasi'

    lokasi = fields.Char('Lokasi')
