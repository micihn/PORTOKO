from odoo import api, fields, models
from datetime import datetime

class ReportStockSparepart(models.TransientModel):
    _name = 'report.stock.sparepart'
    _description = 'Stock Sparepart Wizard'

    date = fields.Datetime()

    def generate_report_sparepart(self):
        products = self.env['product.product'].search([('detailed_type','=','product')])

        product_list = []
        for product in products:
            product_value = 0.00
            product_valuations = self.env['stock.valuation.layer'].search([
                ('product_id', '=', product.id),
                ('create_date', '<=', self.date)
            ])

            for product_valuation in product_valuations:
                product_value += product_valuation.value

            product_dict = {
                'product_code': product.default_code,
                'product_name': product.name,
                'product_price': float(product.list_price),
                'product_qty': float(product.with_context({'to_date': self.date}).qty_available),
                'product_value': float(product_value),
            }
            product_list.append(product_dict)

        data = {'date': self.date.strftime('%d/%m/%Y'),
                'product_list': product_list,
                }

        return self.env.ref('report_sparepart.report_stock_sparepart_action').report_action([], data=data)