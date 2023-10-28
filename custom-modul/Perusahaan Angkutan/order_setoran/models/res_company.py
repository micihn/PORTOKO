from odoo import api, fields, models

class ResCompanySetoranInherit(models.Model):
    _inherit = 'res.company'

    def create_sequence(self, company):

        sequence_data = [
            {
                'name' : 'Order Setoran Sequence - ',
                'code': 'order.setoran.sequence',
                'implementation': 'standard',
                'prefix': 'ST/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },{
                'name' : 'Oper Setoran Sequence - ',
                'code': 'oper.setoran.sequence',
                'implementation': 'standard',
                'prefix': 'SOP/%(day)s/%(month)s/%(year)s',
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
        company = super(ResCompanySetoranInherit, self).create(values)

        self.create_sequence(company)

        return company
