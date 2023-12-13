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

        # if self.fleet_layer == 2:
        #     fleet_settings = self.env['fleet.configuration.service'].search([('company_id', '=', self.company_id.id)])
        #     source_location = fleet_settings.operation_type.default_location_src_id.id
        #     destination_location = fleet_settings.operation_type.default_location_dest_id.id
        #
        #     # picking_permintaan = self.env['stock.picking'].search([('origin', '=', self.origin)])
        #     # picking_permintaan.create_returns()
        #
        #     return_picking = self.env['stock.picking'].create({
        #         'picking_type_id': self.picking_type_id.id,
        #         'location_id': self.location_dest_id.id,
        #         'location_dest_id': self.location_id.id,
        #         'picking_type_id': fleet_settings.operation_type.return_picking_type_id.id,
        #         'origin': 'Return Of' + self.name
        #     })
        #
        #     for move in self.move_ids_without_package:
        #         return_move = self.env['stock.move'].create({
        #             'name': "Return Of" + str(self.fleet_service_id.name),
        #             'product_id': move.product_id.id,
        #             'product_uom_qty': move.product_qty,
        #             'product_uom': move.product_uom.id,
        #             'picking_id': return_picking.id,
        #             'picking_type_id': fleet_settings.operation_type.return_picking_type_id.id,
        #             'location_id': move.location_dest_id.id,
        #             'location_dest_id': move.location_id.id,
        #         })
        #
        #     return_picking.action_confirm()
        #     return_picking.action_assign()
        #     return_picking.button_validate()

        return res

    def button_validate(self):
        res = super(InternalTransferFleet, self).button_validate()
        if self.fleet_layer == 2:
            self.fleet_service_id.state_record = 'selesai'
        elif self.fleet_layer == 1:
            self.fleet_service_id.state_record = 'diminta'
        else:
            pass
        return res