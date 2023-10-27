from odoo import models, api, fields

class KonfigurasiSolarUangMakan(models.Model):
    _name = 'konfigurasi.solar.uang.makan'
    _inherit = ['mail.thread']
    _description = 'Solar Dan Uang Makan'
    _rec_name = 'name'

    name = fields.Char(default="Solar Dan Uang Makan")
    harga_solar = fields.Float(decimal=0)
    uang_makan = fields.Float(decimal=0)
    riwayat = fields.One2many('konfigurasi.solar.uang.makan.riwayat', 'konfigurasi_solar_uang_makan')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def write(self, vals):
        result = super(KonfigurasiSolarUangMakan, self).write(vals)
        riwayat_values = []

        if "uang_makan" in vals:
            riwayat_values.append({
                "tanggal": fields.Datetime.now(),
                "jenis": "Uang Makan",
                "nominal": vals["uang_makan"],
            })

        if "harga_solar" in vals:
            riwayat_values.append({
                "tanggal": fields.Datetime.now(),
                "jenis": "Solar",
                "nominal": vals["harga_solar"],
            })

        if riwayat_values:
            self.env['konfigurasi.solar.uang.makan.riwayat'].create([{
                "konfigurasi_solar_uang_makan": self.id,
                **values,
            } for values in riwayat_values])

        return result

class KonfigurasiSolarUangMakanRiwayat(models.Model):
    _name = 'konfigurasi.solar.uang.makan.riwayat'
    konfigurasi_solar_uang_makan = fields.Many2one('konfigurasi.solar.uang.makan', invisible=True)
    tanggal = fields.Datetime('Tanggal')
    jenis = fields.Char('Jenis')
    nominal = fields.Float('Nominal')