# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Report Sparepart',
    'author': 'Altela Software',
    'version': '0.2',
    'summary': 'Print out report sparepart',
    'license': 'OPL-1',
    'sequence': 1,
    'category': 'Inventory',
    'website': 'https://www.altelasoftware.com',
    'depends': [
        'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_stock_sparepart.xml',
        'report/report_stock_queue_action.xml',
        'report/report_stock_queue_format.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}