from . import models
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):

    def create_konfigurasi_solar_uang_makan(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        for company in companies:
            env['konfigurasi.solar.uang.makan'].create({
                'name': 'Konfigurasi Solar Uang Makan',
                'harga_solar': 0,
                'uang_makan': 0,
                'company_id': company.id,
            })

    def create_konfigurasi_account_uang_jalan(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        for company in companies:
            env['konfigurasi.account.uang.jalan'].create({
                'name': 'Konfigurasi Account',
                'company_id': company.id,
            })

    def create_tipe_muatan(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])
        tipe_muatan = ['Tronton Isi',
                       'Tronton Kosong',
                       'Tronton Dedicated',
                       'Trailer Isi',
                       'Trailer Kosong',
                       'Trailer Dedicated',
                       ]

        for company in companies:
            for trailer in tipe_muatan:
                env['konfigurasi.tipe.muatan'].create({
                    'tipe_muatan': trailer,
                    'company_id': company.id,
                })

    def create_sequence(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        sequence_data = [
            {
                'name' : 'Order Pengiriman Sequence - ',
                'code': 'order.pengiriman.sequence',
                'implementation': 'standard',
                'prefix': 'SO/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },{
                'name' : 'Oper Order Sequence - ',
                'code': 'oper.order.sequence',
                'implementation': 'standard',
                'prefix': 'OP/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },{
                'name' : 'Uang Jalan Sequence - ',
                'code': 'uang.jalan.sequence',
                'implementation': 'standard',
                'prefix': 'UJ/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },{
                'name' : 'Konfigurasi Uang Jalan Sequence - ',
                'code': 'konfigurasi.uang.jalan.sequence',
                'implementation': 'standard',
                'prefix': 'KUJ',
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

    create_konfigurasi_solar_uang_makan(cr, registry)
    create_konfigurasi_account_uang_jalan(cr, registry)
    create_tipe_muatan(cr, registry)
    create_sequence(cr, registry)



