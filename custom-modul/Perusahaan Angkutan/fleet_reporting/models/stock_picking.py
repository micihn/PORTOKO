from odoo import api, models, fields

class InternalTransferFleet(models.Model):
    _inherit = 'stock.picking'

    origin = fields.Char(readonly=True)
    fleet_layer = fields.Integer() # there are 2 layer which the first are 'Permintaan Barang' and the second is 'Barang Keluar'. layer means stock.picking
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services') # fleet service ID (Fleet Module > Fleet > Services), for easier cancellation or any state-changing through picking

    def action_cancel(self):
        res = super(InternalTransferFleet, self).action_cancel()

        self.fleet_service_id.state_record = 'batal'

        fleet_service = self.env['stock.picking'].sudo().search([('name', '=', self.origin)])
        for fleet in fleet_service:
            if fleet.state != 'done':
                fleet.action_cancel()

        return res

    def button_validate(self):
        res = super(InternalTransferFleet, self).button_validate()
        if self.fleet_layer == 2:
            self.fleet_service_id.state_record = 'selesai'
        else:
            self.fleet_service_id.state_record = 'diminta'
        return res