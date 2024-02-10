# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Order Pengiriman',
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
        'views/order_pengiriman.xml',
        'views/konfigurasi_lokasi.xml',
        'views/konfigurasi_tipe_muatan.xml',
        'views/konfigurasi_plant.xml',
        'views/konfigurasi_solar_uang_makan.xml',
        'views/konfigurasi_uang_jalan.xml',
        'views/konfigurasi_account.xml',
        'wizard/close_uang_jalan.xml',
        'views/oper_order.xml',
        'views/fleet_vehicle.xml',
        'views/uang_jalan.xml',
        'views/menu.xml',
        'report/report_uang_jalan.xml',
        'report/report_uang_jalan_action.xml',
    ],
    'demo': [],
    'post_init_hook': 'post_init_hook',
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}