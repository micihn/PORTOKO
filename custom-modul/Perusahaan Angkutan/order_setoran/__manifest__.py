# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Order Setoran',
    'author': 'Altela Software',
    'version': '0.1',
    'summary': 'Pencatatan setoran dari morder pengiriman',
    'license': 'OPL-1',
    'sequence': 1,
    'category': 'Accounting',
    'website': 'https://www.altelasoftware.com',
    'depends': [
        'base',
        'mail',
        'fleet',
        'hr',
        'om_account_accountant',
        'stock',
        'order_pengiriman',
        'web_notify',
        'hr_expense',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/oper_setoran.xml',
        'views/order_setoran.xml',
        'views/konfigurasi_account.xml',
        'data/master_product.xml',
        'wizard/order_setoran_create_invoice.xml',
        'wizard/oper_setoran_create_invoice.xml',
        'wizard/uang_jalan_rincian.xml',
        # 'wizard/create_order_pengiriman.xml',
        'views/menu.xml',
        'report/report_setoran.xml',
        'report/report_komisi_sopir.xml',
        'report/report_komisi_kenek.xml',
        'report/report_setoran_action.xml',
        'report/report_komisi_sopir_action.xml',
        'report/report_komisi_kenek_action.xml',
        'report/uang_jalan_rincian.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}