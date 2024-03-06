from odoo import api, fields, models
from datetime import datetime

class ReportStockSparepart(models.TransientModel):
    _name = 'report.stock.sparepart'
    _description = 'Stock Sparepart Wizard'

    tanggal = fields.Datetime()

    def generate_report_sparepart(self):
        products = self.env['product.product'].search([('detailed_type','=','product')])

        product_list = []
        for product in products:
            product_value = 0
            product_valuation = self.env['stock.valuation.layer'].search([
                ('product_id', '=', product.id),
                ('create_date', '<=', self.tanggal)])
            for product_val in product_valuation:
                product_value += product_val.value

            product_dict = {
                'product_code': product.default_code,
                'product_name': product.name,
                'product_price': float(product.list_price),
                'product_qty': float(product.with_context({'to_date': self.tanggal}).qty_available),
                'product_value': float(product_value),
            }
            product_list.append(product_dict)

            # print(product.with_context({'to_date': self.tanggal}).qty_available)

        data = {'tanggal': self.tanggal.strftime('%d/%m/%Y'),
                'product_list': product_list,
                }

        return self.env.ref('report_sparepart.report_fleet_pendapatan_action').report_action([], data=data)