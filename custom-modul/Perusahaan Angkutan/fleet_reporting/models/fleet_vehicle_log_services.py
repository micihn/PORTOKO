from odoo import fields, models, api

class FleetVehicleLogServiceProduct(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    product_id = fields.Many2one('product.template')
    product_qty = fields.Float('Quantity')
    total_amount = fields.Monetary(compute='_compute_total_amount', store=True)
    is_service = fields.Boolean()
    initial = fields.Boolean(default=True)

    @api.onchange('service_type_id')
    def check_service_type_id_value(self):
        if self.service_type_id.category == 'service':
            self.is_service = True
            self.initial = False
            self.product_qty = 1
            self.amount = 0
            self.total_amount = 0

        elif self.service_type_id.category == 'sparepart':
            self.is_service = False
            self.initial = False
            self.product_qty = 1
            self.amount = 0
            self.total_amount = 0

        elif self.service_type_id.category == 'contract':
            self.is_service = False
            self.initial = False
            self.product_qty = 1
            self.amount = 0
            self.total_amount = 0

    @api.depends('product_qty', 'amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.product_qty * record.amount


class FleetServiceTypeProduct(models.Model):
    _inherit = 'fleet.service.type'

    category = fields.Selection([
        ('service', 'Service'),
        ('sparepart', 'Sparepart'),
    ])