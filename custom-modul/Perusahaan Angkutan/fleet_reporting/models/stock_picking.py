from odoo import api, models, fields
from odoo.exceptions import ValidationError

class InternalTransferFleet(models.Model):
    _inherit = 'stock.picking'

    origin = fields.Char(readonly=True)
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
            if fleet.state_record != 'done':
                fleet.action_cancel()

        fleet_settings = self.env['fleet.configuration.service'].search([('company_id', '=', self.company_id.id)])

        self.fleet_service_id.state_record = 'batal'

        return res

    def button_validate(self):
        self.fleet_service_id.state_record = 'selesai'
        return super(InternalTransferFleet, self).button_validate()


class FleetMove(models.Model):
    _inherit = 'stock.move'


    nomor_kendaraan = fields.Char()
    harga_satuan = fields.Float('Harga Satuan', digits=(6, 0))
    harga_total = fields.Float('Harga Total', digits=(6, 0))

class StockBackorderFleet(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process_cancel_backorder(self):

        service_id = self.env['fleet.vehicle.log.services'].search([('name', '=', self.pick_ids.origin)])

        product_name = []
        for line in self.pick_ids.move_ids:
            # if line.product_uom_qty == line.quantity_done and line.state == 'done':

            service_line = self.env['product.service.line'].search(
                [('product_id', '=', line.product_id.id), ('service', '=', service_id.id)])
            service_line.product_qty = line.quantity_done

            if line.product_uom_qty != line.quantity_done:
                product_name.append(line.product_id.name)

        message = "<p>Log report quantity Updated</p>"
        for name in product_name:
            message += f"<p>- {name}</p>"

        service_id.message_post(body=message)


        return super(StockBackorderFleet, self).process_cancel_backorder()



