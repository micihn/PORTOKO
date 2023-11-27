from odoo import api, fields, models

class ResCompanyKasbonInherit(models.Model):
    _inherit = 'res.company'

    def create_sequence_kasbon(self, company):

        sequence_data = [
            {
                'name' : 'Kasbon Karyawan Sequence - ',
                'code': 'kasbon.karyawan.sequence',
                'implementation': 'standard',
                'prefix': 'PTU/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
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
                'number_next_actual': data['number_next_actual'],
            })

    @api.model
    def create(self, values):
        company = super(ResCompanyKasbonInherit, self).create(values)

        self.create_sequence_kasbon(company)

        return company
