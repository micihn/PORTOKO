from . import models, wizard
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):

    def create_sequence_kasbon(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

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

        for company in companies:
            for data in sequence_data:
                env['ir.sequence'].create({
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

    create_sequence_kasbon(cr, registry)