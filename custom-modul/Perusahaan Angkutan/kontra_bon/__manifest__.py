# -*- coding: utf-8 -*-
{
    'name': "Kontra Bon",

    'summary': """
        Kontra Bon""",

    'description': """
    """,

    'author': "Altela Software",
    'website': "http://www.altelasoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'custom_reports'],

    # always loaded
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/kontra_bon.xml',
        'report/kontra_bon.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}