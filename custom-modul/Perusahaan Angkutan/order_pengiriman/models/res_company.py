from odoo import api, fields, models

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    def create_data_for_company(self, company):
        # Create data records specific to the new company here
        # For example:
        self.env['konfigurasi.solar.uang.makan'].sudo().create({
            'name': 'Konfigurasi Solar Uang Makan',
            'harga_solar': 0,
            'uang_makan': 0,
            'company_id': company.id,
        })

    @api.model
    def create(self, values):
        company = super(ResCompanyInherit, self).create(values)

        # Create the data records for the new company
        self.create_data_for_company(company)

        return company
