# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
from . import models

def post_init_hook(cr, registry):
    def create_sequence_pembayaran_komisi(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

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

        for company in companies:
            env['konfigurasi.komisi'].sudo().create({
                'name': 'Konfigurasi Komisi',
                'company_id': company.id,
            })

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
                })

    def create_sequence_tabung_komisi(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        sequence_data = [
            {
                'name' : 'Nomor Tabung Komisi - ',
                'code': 'tabung.komisi',
                'implementation': 'standard',
                'prefix': 'PT',
                'padding': 7,
                'number_increment': 1,
            }
        ]

        for company in companies:
            env['konfigurasi.komisi'].sudo().create({
                'name': 'Konfigurasi Komisi',
                'company_id': company.id,
            })

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
                })

    def create_sequence_tabungan_ptu(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])

        sequence_data = [
            {
                'name' : 'Tabungan PTU Sequence - ',
                'code': 'tabungan.ptu.sequence',
                'implementation': 'standard',
                'prefix': 'KMM',
                'padding': 6,
                'number_increment': 1,
            }
        ]

        for company in companies:
            env['konfigurasi.komisi'].sudo().create({
                'name': 'Konfigurasi Komisi',
                'company_id': company.id,
            })

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
                })


    create_sequence_pembayaran_komisi(cr, registry)
    create_sequence_tabung_komisi(cr, registry)
    create_sequence_tabungan_ptu(cr, registry)
