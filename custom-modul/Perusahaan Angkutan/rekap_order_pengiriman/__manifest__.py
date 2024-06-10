# -*- coding: utf-8 -*-
{
    'name': "Rekapan Order Pengiriman",

    'summary': """
        Rekap Order / Oper Order Pengiriman""",

    'description': """
    """,

    'author': "Altela Software",
    'website': "https://www.altelasoftware.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'order_pengiriman', 'order_setoran'],

    # always loaded
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/rekap_order.xml',
        'report/rekap_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}