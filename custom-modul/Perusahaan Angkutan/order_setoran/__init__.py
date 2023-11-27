from . import models, wizard
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):

    def create_sequence_setoran(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

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
                'prefix': 'SOP/%(day)s/%(month)s/%(year)s/',
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

    def create_konfigurasi_account_setoran(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        for company in companies:
            env['konfigurasi.account.setoran'].create({
                'name': 'Konfigurasi Account',
                'company_id': company.id,
            })

    create_sequence_setoran(cr, registry)
    create_konfigurasi_account_setoran(cr, registry)