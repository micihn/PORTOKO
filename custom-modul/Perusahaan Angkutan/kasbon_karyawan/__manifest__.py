# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Kasbon Karyawan',
    'author': 'Altela Software',
    'version': '0.1',
    'summary': 'Pencatatan hutang karyawan dan pelunasannya',
    'license': 'OPL-1',
    'sequence': 1,
    'category': 'Accounting',
    'website': 'https://www.altelasoftware.com',
    'depends': [
        'om_account_accountant',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/kasbon_karyawan.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}