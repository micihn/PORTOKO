from . import models
from . import wizard

from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):

    def create_sequence_service(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        sequence_data = [
            {
                'name' : 'Permintaan Barang Sequence - ',
                'code': 'permintaan.barang.sequence',
                'implementation': 'standard',
                'prefix': 'PB/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },

            {
                'name': 'Service Sequence - ',
                'code': 'service.sequence',
                'implementation': 'standard',
                'prefix': 'SE/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },
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

    def create_service_type(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        types = [{
                'name': 'BAN',
                'category': 'sparepart',
                },{
                'name': 'KABIN',
                'category': 'sparepart',
                },{
                'name': 'MEKANIK',
                'category': 'sparepart',
                },{
                'name': 'OLI',
                'category': 'sparepart',
                },{
                'name': 'Expense Lain-lain',
                'category': 'service',
            }]

        for company in companies:
            for item in types:
                print(item['name'])
                print(item['category'])
                env['fleet.service.type'].create({
                    'name': item['name'],
                    'category': item['category'],
                    'company_id': company.id,
                })

    def create_fleet_setting(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        for company in companies:
            env['fleet.configuration.service'].create({
                'name': 'Konfigurasi Service',
                'company_id': company.id,
            })

    create_fleet_setting(cr, registry)
    create_service_type(cr, registry)
    create_sequence_service(cr, registry)
