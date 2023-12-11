from odoo import fields, models, api
from odoo.exceptions import ValidationError

class FleetVehicleLogServiceProduct(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _rec_name = 'name'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('service.sequence') or 'New'
        result = super(FleetVehicleLogServiceProduct, self).create(vals)
        return result

    name = fields.Char(readonly=True, required=True, copy=False, default='New')
    product_id = fields.Many2one('product.product')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    product_qty = fields.Float('Quantity')
    total_amount = fields.Monetary(compute='_compute_total_amount', store=True)
    is_service = fields.Boolean()
    initial = fields.Boolean(default=True)
    description = fields.Char(required=True)
    state_record = fields.Selection([
        ('draft', 'Draft'),
        ('diminta', 'Diminta'),
        ('selesai', 'Selesai'),
        ('batal', 'Batal'),
    ], default='draft', string='Stage', group_expand='_expand_states', copy=False)

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

    def validate(self):
        account_settings = self.env['fleet.configuration.service'].search([('company_id', '=', self.company_id.id)])
        if bool(account_settings.operation_type) == False:
            raise ValidationError('Anda belum melakukan pengaturan pada Fleet > Configuration > Service > Configuration')

        if self.is_service:
            # bikin expenses
            pass
        else:
            picking = self.env['stock.picking'].create({
                'location_id': account_settings.operation_type.default_location_src_id.id,
                'location_dest_id': account_settings.operation_type.default_location_dest_id.id,
                'picking_type_id': account_settings.operation_type.id,
                'origin': self.name
            })
            move_receipt_1 = self.env['stock.move'].create({
                'name': self.name + str(' - ' + self.description),
                'product_id': self.product_id.id,
                # 'quantity_done': self.product_qty,
                'product_uom': self.product_id.product_tmpl_id.uom_id.id,
                'picking_id': picking.id,
                'picking_type_id': account_settings.operation_type.id,
                'location_id': account_settings.operation_type.default_location_src_id.id,
                'location_dest_id': account_settings.operation_type.default_location_dest_id.id,
            })
            move_receipt_1._action_confirm()
            move_receipt_1._action_assign()

            print(picking.name)
            picking.fleet_layer = 1
            picking.fleet_service_id = self.id

            related_picking = self.env['stock.picking'].search([('origin', '=', picking.name)])
            for rec in related_picking:
                print(rec)
                rec.fleet_layer = 2
                rec.fleet_service_id = self.id

        self.state_record = 'diminta'

    def cancel(self):
        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name)])
        for picking in stock_picking:
            picking.action_cancel()
        self.state_record = 'batal'

    def cancel_from_picking(self):
        self.state_record = 'batal'

class FleetServiceTypeProduct(models.Model):
    _inherit = 'fleet.service.type'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)


    category = fields.Selection([
        ('service', 'Service'),
        ('sparepart', 'Sparepart'),
    ])