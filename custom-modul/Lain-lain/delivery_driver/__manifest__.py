{
    'name': 'Delivery Driver',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Show driver and vehicle information from fleet module into Inventory Delivery.',
    'description': """Show driver and vehicle information from fleet module Inventory Delivery.""",
    'depends': ['fleet', 'stock', 'hr'],
    'author': 'Altela Software',
    'license': 'OPL-1',
    'website': 'www.altelasoftware.com',
    'data': [
        'security/ir.model.access.csv',
        'report/report_picking.xml',
        'views/stock_picking.xml',
    ],
    'application': False,
}
