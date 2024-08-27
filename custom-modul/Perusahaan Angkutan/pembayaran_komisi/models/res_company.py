from odoo import api, fields, models

class ResCompanyPengirimanInherit(models.Model):
    _inherit = 'res.company'

    def create_konfigurasi_komisi(self, company):
        self.env['konfigurasi.komisi'].sudo().create({
            'name': 'Konfigurasi Komisi',
            'company_id': company.id,
        })

    @api.model
    def create(self, values):
        company = super(ResCompanyPengirimanInherit, self).create(values)

        self.create_konfigurasi_komisi(company)

        return company
