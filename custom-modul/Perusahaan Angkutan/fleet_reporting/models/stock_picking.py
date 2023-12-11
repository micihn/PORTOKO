from odoo import api, models, fields

class InternalTransferFleet(models.Model):
    _inherit = 'stock.picking'

    origin = fields.Char(readonly=True)
    fleet_layer = fields.Integer()
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services')

    def action_cancel(self):
        res = super(InternalTransferFleet, self).action_cancel()

        # First level picking cancellation
        fleet_service = self.env['fleet.vehicle.log.services'].sudo().search([('name', '=', self.origin)])
        for fleet in fleet_service:
            fleet.cancel_from_picking()

        return res


    def button_validate(self):
        res = super(InternalTransferFleet, self).button_validate()
        if self.fleet_layer == 2:
            self.fleet_service_id.state_record = 'selesai'
        return res