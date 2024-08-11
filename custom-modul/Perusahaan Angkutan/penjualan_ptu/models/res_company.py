from odoo import api, fields, models

class ResCompanyPenjualanPTUInherit(models.Model):
    _inherit = 'res.company'

    def create_konfigurasi_penjualan_ptu(self, company):
        self.env['penjualan.ptu'].sudo().create({
            'name': 'Konfigurasi Penjualan PTU',
            'company_id': company.id,
        })

    @api.model
    def create(self, values):
        company = super(ResCompanyPenjualanPTUInherit, self).create(values)

        self.create_konfigurasi_penjualan_ptu(company)

        return company
