# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Uang Jalan',
    'author': 'Altela Software',
    'version': '0.2',
    'summary': 'Pencatatan serta tracking pengiriman',
    'license': 'OPL-1',
    'sequence': 1,
    'category': 'Sales',
    'website': 'https://www.altelasoftware.com',
    'depends': [
        'base',
        'mail',
        'fleet',
        'hr',
        'web_notify',
        'om_account_accountant',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/report_paperformat.xml',
        'views/order_pengiriman.xml',
        'views/konfigurasi_lokasi.xml',
        'views/konfigurasi_tipe_muatan.xml',
        'views/konfigurasi_plant.xml',
        'views/konfigurasi_solar_uang_makan.xml',
        'views/konfigurasi_uang_jalan.xml',
        'views/konfigurasi_account.xml',
        'wizard/close_uang_jalan.xml',
        'wizard/uang_jalan_gantung.xml',
        'views/oper_order.xml',
        'views/fleet_vehicle.xml',
        'views/uang_jalan.xml',
        'report/report_uang_jalan.xml',
        'report/report_uang_jalan_tutup.xml',
        'report/report_uang_jalan_action.xml',
        'report/report_uang_jalan_gantung.xml',
        'report/report_uang_jalan_gantung_action.xml',
        'views/menu.xml',

    ],
    'demo': [],
    'post_init_hook': 'post_init_hook',
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}