from odoo import fields, models, api

class FleetVehicleLogServiceProduct(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    product_id = fields.Many2one('product.template')
    product_qty = fields.Float('Quantity')
    total_amount = fields.Monetary(compute='_compute_total_amount', store=True)

    @api.depends('product_qty', 'amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.product_qty * record.amount