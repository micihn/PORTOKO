from odoo import api, fields, models

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    def create_konfigurasi_solar_uang_makan(self, company):
        self.env['konfigurasi.solar.uang.makan'].sudo().create({
            'name': 'Konfigurasi Solar Uang Makan',
            'harga_solar': 0,
            'uang_makan': 0,
            'company_id': company.id,
        })

    def create_tipe_muatan(self, company):
        tipe_muatan = ['Tronton Isi',
                       'Tronton Kosong',
                       'Tronton Dedicated',
                       'Trailer Isi',
                       'Trailer Kosong',
                       'Trailer Dedicated',
                       ]

        for muatan in tipe_muatan:
            self.env['konfigurasi.tipe.muatan'].sudo().create({
                'tipe_muatan': muatan,
                'company_id': company.id,
            })

    @api.model
    def create(self, values):
        company = super(ResCompanyInherit, self).create(values)

        self.create_konfigurasi_solar_uang_makan(company)
        self.create_tipe_muatan(company)

        return company
