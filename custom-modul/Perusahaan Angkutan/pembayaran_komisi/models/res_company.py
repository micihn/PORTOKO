from odoo import api, fields, models

class ResCompanyPengirimanInherit(models.Model):
    _inherit = 'res.company'

    def create_konfigurasi_komisi(self, company):
        self.env['konfigurasi.komisi'].sudo().create({
            'name': 'Konfigurasi Komisi',
            'company_id': company.id,
        })

    def create_sequence_bayar_komisi(self, company):
        sequence_data = [
            {
                'name' : 'Nomor Bayar Komisi - ',
                'code': 'bayar.komisi',
                'implementation': 'standard',
                'prefix': 'KM',
                'padding': 7,
                'number_increment': 1,
            }
        ]

        for data in sequence_data:
            self.env['ir.sequence'].create({
                'name': data['name'] + str(company.name),
                'code': data['code'],
                'implementation': data['implementation'],
                'active': 'True',
                'company_id': company.id,
                'prefix': data['prefix'],
                'padding': data['padding'],
                'number_increment': data['number_increment'],
            })

    def create_sequence_tabung_komisi(self, company):
        sequence_data = [
            {
                'name' : 'Tabung Komisi - ',
                'code': 'tabung.komisi',
                'implementation': 'standard',
                'prefix': 'PT',
                'padding': 7,
                'number_increment': 1,
            }
        ]

        for data in sequence_data:
            self.env['ir.sequence'].create({
                'name': data['name'] + str(company.name),
                'code': data['code'],
                'implementation': data['implementation'],
                'active': 'True',
                'company_id': company.id,
                'prefix': data['prefix'],
                'padding': data['padding'],
                'number_increment': data['number_increment'],
            })


    @api.model
    def create(self, values):
        company = super(ResCompanyPengirimanInherit, self).create(values)

        self.create_konfigurasi_komisi(company)

        self.create_konfigurasi_komisi(company)

        self.create_sequence_bayar_komisi(company)

        return company






