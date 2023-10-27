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

    create_konfigurasi_solar_uang_makan(cr, registry)
    create_tipe_muatan(cr, registry)


