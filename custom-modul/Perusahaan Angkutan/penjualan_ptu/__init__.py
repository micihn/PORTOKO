# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
from . import models

def post_init_hook(cr, registry):
    def create_konfigurasi_penjualan_ptu(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        for company in companies:
            env['konfigurasi.penjualan.ptu'].sudo().create({
                'name': 'Konfigurasi Penjualan PTU',
                'company_id': company.id,
            })

    create_konfigurasi_penjualan_ptu(cr, registry)



