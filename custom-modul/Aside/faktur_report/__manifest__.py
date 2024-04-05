# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Faktur Report',
    'author': 'Altela Software',
    'version': '16.0.1.0.0',
    'summary': 'A module to generate custom Invoice Faktur',
    'license': 'LGPL-3',
    'sequence': 1,
    'description': """A module to generate custom Invoice Faktur""",
    'category': 'Accounting',
    'website': 'https://www.altelasoftware.com',
    'depends': [
        'account',
    ],
    'data': [
        'report/report.xml',
        'report/faktur_template.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
