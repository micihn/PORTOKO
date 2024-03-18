from odoo import api, models, fields
from odoo.exceptions import ValidationError

class InternalTransferFleet(models.Model):
    _inherit = 'stock.picking'

    origin = fields.Char(readonly=True)
    fleet_layer = fields.Integer() # there are 2 'layer' which the first are 'Permintaan Barang' and the second is 'Barang Keluar'. layer means stock.picking
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services') # fleet service ID (Fleet Module > Fleet > Services), for easier cancellation or any state-changing through picking
    is_permintaan_barang = fields.Boolean()
    nominal_permintaan = fields.Float('Harga Satuan', digits=(6, 0), compute="compute_nominal_permintaan")
    group_id = fields.Many2one(readonly=False)

    @api.depends('move_ids_without_package.harga_total')
    def compute_nominal_permintaan(self):
        for record in self:
            total_harga = sum(record.move_ids_without_package.mapped('harga_total'))
            record.nominal_permintaan = total_harga

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

class StockBackorderFleet(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process_cancel_backorder(self):

        if self.pick_ids.fleet_layer == 1:
            service_id = self.env['fleet.vehicle.log.services'].search([('name', '=', self.pick_ids.origin)])

            product_name = []
            for line in self.pick_ids.move_ids:
                # if line.product_uom_qty == line.quantity_done and line.state == 'done':

                service_line = self.env['product.service.line'].search([('product_id', '=', line.product_id.id), ('service','=', service_id.id)])
                service_line.product_qty = line.quantity_done

                if line.product_uom_qty != line.quantity_done:
                    product_name.append(line.product_id.name)

            # raise ValidationError("Tes")

            # for line in self.pick_ids.move_line_ids_without_package:
            #
            #     if line.product_uom_qty == line.quantity_done and line.state == 'done':
            #         service_line = self.env['product.service.line'].search([('product_id', '=', line.product_id.id), ('service','=',service_id.id)])
            #         service_line.product_qty = line.quantity_done
            #         product_name.append(line.product_id.name)

            message = "<p>Log report quantity Updated</p>"
            for name in product_name:
                message += f"<p>- {name}</p>"

            service_id.message_post(body=message)

        return super(StockBackorderFleet, self).process_cancel_backorder()



