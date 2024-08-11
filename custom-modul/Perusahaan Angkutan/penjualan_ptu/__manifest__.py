# -*- coding: utf-8 -*-
{
    'name': "Penjualan PTU",
    'summary': """
        Penjualan PTU""",
    'description': """
        Fitur penjualan PTU
    """,
    'author': "Altela Software",
    'website': "https://www.altelasoftware.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base', 'order_setoran', 'om_account_accountant'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/penjualan_ptu.xml',
        'views/konfigurasi_penjualan_ptu.xml',
        'views/menu.xml',
    ],
    'depends':[
        'stock',
        'pembayaran_komisi'
    ],
    'post_init_hook': 'post_init_hook',
    'demo': [],
}