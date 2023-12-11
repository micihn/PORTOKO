# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Fleet Reporting',
    'author': 'Altela Software',
    'version': '0.1',
    'summary': 'Reporting untuk fleet (kendaraan) dan juga beberapa tambahan lain',
    'license': 'OPL-1',
    'sequence': 1,
    'category': 'Fleet',
    'website': 'https://www.altelasoftware.com',
    'depends': [
        'fleet',
        'hr_fleet',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/fleet_vehicle_log_services.xml',
        'views/fleet_configuration_service.xml',
        'views/stock_picking.xml',
        'wizard/service_fleet_report.xml',
        'report/report_service_fleet.xml',
        'report/report_service_fleet_action.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}