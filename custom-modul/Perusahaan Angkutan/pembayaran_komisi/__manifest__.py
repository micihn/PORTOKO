# -*- coding: utf-8 -*-
{
    'name': "Pembayaran Komisi",

    'summary': """
        Pembayaran Komisi""",

    'description': """
        Fitur pembayaran komisi serta tabungan komisi.
    """,

    'author': "Altela Software",
    'website': "https://www.altelasoftware.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'order_setoran', 'om_account_accountant'],

    # always loaded
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/product_product.xml',
        'views/hr_employee.xml',
        'views/bayar_komisi.xml',
        'views/tabung_komisi.xml',
        'views/konfigurasi.xml',
        'views/menu.xml',
    ],
    'post_init_hook': 'post_init_hook',
    # only loaded in demonstration mode
    'demo': [],
}