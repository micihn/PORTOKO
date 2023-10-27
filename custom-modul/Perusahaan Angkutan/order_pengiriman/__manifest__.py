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
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/order_pengiriman.xml',
        'views/konfigurasi_lokasi.xml',
        'views/konfigurasi_plant.xml',
        'views/konfigurasi_solar_uang_makan.xml',
        'views/konfigurasi_uang_jalan.xml',
        'views/oper_order.xml',
        'views/uang_jalan.xml',
        'views/menu.xml',
        'views/sequences.xml',
        # 'data/konfigurasi_solar_uang_makan_data.xml',
    ],
    'demo': [],
    'post_init_hook': 'post_init_hook',
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}