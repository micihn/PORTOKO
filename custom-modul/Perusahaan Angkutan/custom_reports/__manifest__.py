# -*- coding: utf-8 -*-
{
    'name': "Custom Reports",

    'summary': """
        Custom reports for Invoices, Vendor Bills and Product Move
    """,

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
    'depends': ['base', 'sale_management', 'purchase', 'account', 'stock', 'sale_order_line_multi_warehouse'],

    # always loaded
    'data': [
        'data/report_paperformat.xml',
        'report/surat_jalan.xml',
        'report/do_pengambilan.xml',
        'report/retur_penjualan.xml',
        'report/bukti_pembayaran_hutang.xml',
        'report/penerimaan_piutang.xml',
        'report/faktur.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}