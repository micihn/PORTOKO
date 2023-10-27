from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
import re

class OperOrder(models.Model):
    _name = 'oper.order'
    _description = 'Oper Order'
    _inherit = ['mail.thread']
    _rec_name = 'oper_order_name'

    active = fields.Boolean('Archive', default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    # Method untuk auto name assignment
    @api.model
    def create(self, vals):
        if vals.get('oper_order_name', 'New') == 'New':
            vals['oper_order_name'] = self.env['ir.sequence'].next_by_code('oper.order.sequence') or 'New'
        result = super(OperOrder, self).create(vals)
        return result

    @api.depends('kendaraan')
    def _compute_kendaraan_orm(self):
        for record in self:
            record.kendaraan_orm = str(record.kendaraan).replace(" ", "").lower()

    def confirm_to_request(self):
        for record in self:
            if bool(record.vendor_pa) == False:
                raise ValidationError('Harap isi Vendor PA sebelum mengkonfirmasi!')
            elif bool(record.kendaraan) == False:
                raise ValidationError('Harap isi Kendaraan sebelum mengkonfirmasi!')
            elif not record.oper_order_line:
                raise ValidationError('Anda belum memasukkan nomor Order Pengiriman!')
            else:
                record.state = 'requested'

    def validate(self):
        for record in self.oper_order_line:
            record.order_pengiriman.write({
                'is_sudah_disetor': False,
                'is_oper_order': True,
                'state': 'dalam_perjalanan',
                'oper_order': self.id,
                'vendor_pa': self.vendor_pa.id,
                'nomor_kendaraan': self.kendaraan,
            })
        self.state = 'confirmed'

    def cancel(self):
        for record in self.oper_order_line:
            record.order_pengiriman.write({
                'is_sudah_disetor': False,
                'is_oper_order': False,
                'state': 'order_baru',
                'oper_order': None,
                'vendor_pa': None,
                'nomor_kendaraan': None,
                'model_kendaraan': None,
            })

        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'to_request'

    # fields definition
    oper_order_name = fields.Char(readonly=True, required=True, copy=False, default='New')
    vendor_pa = fields.Many2one('res.partner', states={
        'to_request': [('readonly', False)],
        'requested': [('readonly', True)],
        'confirmed': [('readonly', True)],
        'cancel': [('readonly', True)],
    })
    kendaraan = fields.Char('Kendaraan', states={
        'to_request': [('readonly', False)],
        'requested': [('readonly', True)],
        'confirmed': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    kendaraan_orm = fields.Char('Kendaraan (ORM)', compute='_compute_kendaraan_orm', store=True)

    biaya_total = fields.Float('Total', compute='_compute_biaya', store=True)
    oper_order_line = fields.One2many('oper.order.line', 'oper_order', required = True, states={
        'to_request': [('readonly', False)],
        'requested': [('readonly', True)],
        'confirmed': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    state = fields.Selection([
        ('to_request', "To Request"),
        ('requested', "Requested"),
        ('confirmed', "Confirmed"),
        ('cancel', "Cancelled"),
    ], default='to_request', string="State", index=True, hide=True, tracking=True)

    def unlink(self):
        if any(record.state not in ('to_request', 'cancel') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'To Request' atau 'Cancel'.")

        return super(OperOrder, self).unlink()

    # Method untuk menghitung subtotal ongkos jenis order DO
    @api.depends('oper_order_line.subtotal_biaya')
    def _compute_biaya(self):
        for record in self:
            record.biaya_total = sum(record.oper_order_line.mapped('subtotal_biaya'))

class OperOrderLine(models.Model):
    _name = 'oper.order.line'
    _description = 'Oper Order Line'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    oper_order = fields.Many2one('oper.order', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'No Order', domain=[('state', '=', 'order_baru')])
    muat = fields.Many2one('konfigurasi.lokasi', 'Muat', compute='_compute_muat_and_bongkar', store=True)
    bongkar = fields.Many2one('konfigurasi.lokasi', 'Bongkar', compute='_compute_muat_and_bongkar', store=True)
    keterangan = fields.Text('Keterangan')
    subtotal_biaya = fields.Float('Subtotal Biaya')

    @api.depends('order_pengiriman.alamat_muat', 'order_pengiriman.alamat_bongkar')
    def _compute_muat_and_bongkar(self):
        for record in self:
            record.muat = record.order_pengiriman.alamat_muat
            record.bongkar = record.order_pengiriman.alamat_bongkar

