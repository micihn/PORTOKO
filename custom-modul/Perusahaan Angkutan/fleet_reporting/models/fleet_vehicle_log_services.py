from odoo import fields, models, api
from odoo.exceptions import ValidationError

class FleetVehicleLogServiceProduct(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _rec_name = 'name'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            service_type = self.env['fleet.service.type'].search([('id', '=', vals['service_type_id'])])
            if service_type.category == 'service':
                vals['name'] = self.env['ir.sequence'].next_by_code('service.sequence') or 'New'
            elif service_type.category == 'sparepart':
                vals['name'] = self.env['ir.sequence'].next_by_code('permintaan.barang.sequence') or 'New'

        result = super(FleetVehicleLogServiceProduct, self).create(vals)
        return result

    def return_product(self):
        action = self.env.ref('fleet_reporting.action_return_product_service').read()[0]
        action['views'] = [(self.env.ref('fleet_reporting.return_product_service_view').id, 'form')]
        return action

    name = fields.Char(readonly=True, required=True, copy=False, default='New')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    total_amount = fields.Monetary(readonly=False, store=True, copy=False, default=0)
    is_service = fields.Boolean()
    amount = fields.Monetary(copy=False, readonly=True, compute="compute_amount", default=0)
    initial = fields.Boolean(default=True)
    description = fields.Char(required=True)
    account_expense = fields.Many2one('account.account', string='Account Expenses')
    account_journal = fields.Many2one('account.journal', string='Account Journal')
    state_record = fields.Selection([
        ('draft', 'Draft'),
        ('diminta', 'Diminta'),
        ('selesai', 'Selesai'),
        ('batal', 'Batal'),
    ], default='draft', string='Stage', group_expand='_expand_states', copy=False)

    list_sparepart = fields.One2many('product.service.line', 'service', copy=False)

    @api.depends('list_sparepart.total_cost')
    def compute_amount(self):
        for services in self:
            if services.service_type_id.category == 'sparepart':
                total_cost_product = 0
                for line in services.list_sparepart:
                    total_cost_product += line.total_cost
                services.amount = total_cost_product
            elif services.service_type_id.category == 'service':
                services.amount = services.total_amount

    @api.onchange('service_type_id')
    def check_service_type_id_value(self):
        if self.service_type_id.category == 'service':
            self.is_service = True
            self.initial = False
            self.amount = 0
            self.total_amount = 0
        elif self.service_type_id.category == 'sparepart':
            self.is_service = False
            self.initial = False
            self.total_amount = 0
        elif self.service_type_id.category == 'contract':
            self.is_service = False
            self.initial = False
            self.total_amount = 0

    def validate(self):
        fleet_settings = self.env['fleet.configuration.service'].search([('company_id', '=', self.company_id.id)])
        if not fleet_settings.operation_type:
            raise ValidationError('Anda belum melakukan pengaturan pada Fleet > Configuration > Service > Configuration')

        if self.is_service:
            journal_entry_hutang = self.env['account.move'].sudo().create({
                'company_id': self.company_id.id,
                'move_type': 'entry',
                'date': self.date,
                'ref': f'{self.name} - {self.description}',
                'journal_id': self.account_journal.id,
                'line_ids': [
                    (0, 0, {
                        'name': self.name,
                        'date': self.date,
                        'account_id': self.account_expense.id,
                        'company_id': self.company_id.id,
                        'debit': self.total_amount,
                    }),
                    (0, 0, {
                        'name': self.name,
                        'date': self.date,
                        'account_id': self.account_journal.default_account_id.id,
                        'company_id': self.company_id.id,
                        'credit': self.total_amount,
                    }),
                ],
            })
            journal_entry_hutang.action_post()
            self.state_record = 'selesai'
        else:
            for line in self.list_sparepart:
                if line.product_qty == 0:
                    raise ValidationError(f'Qty Produk {line.product_id.name} berisi 0')

                if line.available_qty < line.product_qty:
                    raise ValidationError(f'Qty Produk {line.product_id.name} lebih sedikit dari yang tersedia.')

            spareparts = [line.product_id.id for line in self.list_sparepart]
            duplicates = list(filter(lambda x: spareparts.count(x) > 1, set(spareparts)))

            if duplicates:
                raise ValidationError("Terdapat produk sparepart duplikat dalam list")

            picking = self.env['stock.picking'].create({
                'partner_id': self.purchaser_id.id,
                'location_id': fleet_settings.operation_type.default_location_src_id.id,
                'location_dest_id': fleet_settings.operation_type.default_location_dest_id.id,
                'picking_type_id': fleet_settings.operation_type.id,
                'origin': self.name,
                'is_permintaan_barang': True,
            })

            for line in self.list_sparepart:
                stock_move = self.env['stock.move'].create({
                    'name': f'{self.name} - {self.description}',
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_id.product_tmpl_id.uom_id.id,
                    'picking_id': picking.id,
                    'nomor_kendaraan': self.vehicle_id.license_plate,
                    'harga_satuan': line.cost,
                    'harga_total': line.total_cost,
                    'picking_type_id': fleet_settings.operation_type.id,
                    'location_id': fleet_settings.operation_type.default_location_src_id.id,
                    'location_dest_id': fleet_settings.operation_type.default_location_dest_id.id,
                })
                stock_move._action_confirm()
                stock_move._action_assign()
                
            line.product_return_limit = line.product_qty
            picking.fleet_service_id = self.id
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


class ProductLine(models.Model):
    _name = 'product.service.line'
    _description = 'Product Service Line'

    service = fields.Many2one('fleet.vehicle.log.services', invisible=True)
    product_id = fields.Many2one('product.product', copy=False, domain="[('qty_available', '>', 0)]")  # Add domain here
    product_qty = fields.Float()
    available_qty = fields.Float("Qty Tersedia", compute="get_available_qty")
    product_return_limit = fields.Float()
    cost = fields.Float()
    total_cost = fields.Float(compute='_compute_total_cost', store=True, copy=False, default=0)

    @api.depends('product_id', 'product_qty', 'cost')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.product_qty * record.cost

    @api.onchange('product_id')
    def define_cost(self):
        for rec in self:
            rec.cost = rec.product_id.product_tmpl_id.standard_price or 0

    @api.depends('product_id')
    def get_available_qty(self):
        for rec in self:
            fleet_settings = self.env['fleet.configuration.service'].search([('company_id', '=', self.env.company.id)], limit=1)
            if rec.product_id.id and fleet_settings and fleet_settings.operation_type:
                available_qty = self.env['stock.quant'].sudo()._get_available_quantity(
                    rec.product_id,
                    fleet_settings.operation_type.default_location_src_id,
                    strict=True
                )
                rec.available_qty = available_qty
            else:
                rec.available_qty = 0
