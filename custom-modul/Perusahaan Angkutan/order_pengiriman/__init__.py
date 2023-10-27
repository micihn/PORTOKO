from . import models
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    _logger.info("post_init_hook is running.")

    create_company_specific_data(cr, registry)

def create_company_specific_data(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])

    for company in companies:
        print("Aal", company)
        # Create a record for each company
        env['konfigurasi.solar.uang.makan'].create({
            'name': 'Konfigurasi Solar Uang Makan',
            'harga_solar': 0,
            'uang_makan': 0,
            'company_id': company.id,
        })


