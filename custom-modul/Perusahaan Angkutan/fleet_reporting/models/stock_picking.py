from odoo import api, models, fields

class InternalTransferFleet(models.Model):
    _inherit = 'stock.picking'

    origin = fields.Char(readonly=True)
    fleet_layer = fields.Integer() # there are 2 'layer' which the first are 'Permintaan Barang' and the second is 'Barang Keluar'. layer means stock.picking
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services') # fleet service ID (Fleet Module > Fleet > Services), for easier cancellation or any state-changing through picking
    nominal_permintaan = fields.Float('Harga Satuan', digits=(6, 0), compute="compute_nominal_permintaan")
    is_permintaan_barang = fields.Boolean()

    @api.depends('move_ids_without_package.harga_total')
    def compute_nominal_permintaan(self):
        for record in self.move_ids_without_package:
            self.nominal_permintaan += record.harga_total


    def action_cancel(self):
        res = super(InternalTransferFleet, self).action_cancel()

        fleet_service = self.env['stock.picking'].sudo().search([('name', '=', self.origin)])
        for fleet in fleet_service:
            if fleet.state != 'done':
                fleet.action_cancel()

        if self.fleet_layer == 2:
            fleet_settings = self.env['fleet.configuration.service'].search([('company_id', '=', self.company_id.id)])

            return_picking = self.env['stock.picking'].create({
                'picking_type_id': fleet_settings.return_operation_type.id,
                'location_id': fleet_settings.return_operation_type.default_location_src_id.id,
                'location_dest_id': fleet_settings.return_operation_type.default_location_dest_id.id,
                'origin': 'Return Of' + self.name
            })

            for move in self.move_ids_without_package:
                return_move = self.env['stock.move'].create({
                    'name': "Return Of " + str(self.fleet_service_id.name),
                    'product_id': move.product_id.id,
                    'quantity_done': move.product_qty,
                    'product_uom': move.product_uom.id,
                    'picking_id': return_picking.id,
                    'picking_type_id': fleet_settings.return_operation_type.id,
                    'location_id': fleet_settings.return_operation_type.default_location_src_id.id,
                    'location_dest_id': fleet_settings.return_operation_type.default_location_dest_id.id,
                })

                return_move._action_confirm()
                return_move._action_assign()

        self.fleet_service_id.state_record = 'batal'

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


class FleetMove(models.Model):
    _inherit = 'stock.move'


    nomor_kendaraan = fields.Char()
    harga_satuan = fields.Float('Harga Satuan', digits=(6, 0))
    harga_total = fields.Float('Harga Total', digits=(6, 0))



