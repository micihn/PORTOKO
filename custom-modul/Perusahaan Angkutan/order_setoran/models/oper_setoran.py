from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import re

class OperSetoran(models.Model):
    _name = 'oper.setoran'
    _description = 'Oper Setoran'
    _inherit = ['mail.thread']
    _rec_name = 'kode_oper_setoran'

    kode_oper_setoran = fields.Char(readonly=True, required=True, copy=False, default='New')
    total_jumlah = fields.Float(compute='_compute_jumlah', digits=(6, 0))
    total_bayar_dimuka = fields.Float(compute='_compute_total_bayar_dimuka', digits=(6, 0))
    total_pendapatan = fields.Float(digits=(6, 0))
    total_pembelian = fields.Float(compute='_compute_total_pembelian', digits=(6, 0))
    total_biaya_fee = fields.Float(compute='_compute_total_biaya_fee', digits=(6, 0))
    total_oper_order = fields.Float(compute='_compute_jumlah_oper_order', digits=(6, 0))
    total_list_pembelian = fields.Float(compute='_compute_jumlah_list_pembelian', digits=(6, 0))
    sisa = fields.Float(compute='_calculate_sisa', digits=(6, 0))
    # komisi_sopir = fields.Float(compute='_compute_komisi_sopir', digits=(6, 0))
    # komisi_kenek = fields.Float(compute='_compute_komisi_kenek', digits=(6, 0))

    vendor_pa = fields.Many2one('res.partner', 'Vendor PA', required=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    kendaraan = fields.Char('Kendaraan', required=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    tanggal_stlo = fields.Date('Tanggal STL/O', states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })
    tanggal_oper = fields.Date('Tanggal Oper', states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })
    keterangan = fields.Text('Keterangan', states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    state = fields.Selection([
        ('draft', "Draft"),
        ('done', "Done"),
        ('cancel', "cancel")
    ], default='draft', string="State", index=True, hide=True, tracking=True)

    detail_order = fields.One2many('detail.order.setoran', 'oper_setoran', copy=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    list_oper_order = fields.One2many('list.oper.order.setoran', 'oper_setoran', copy=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    list_pembelian_setoran = fields.One2many('list.pembelian.setoran', 'oper_setoran', copy=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    biaya_fee_setoran = fields.One2many('biaya.fee.setoran', 'oper_setoran', copy=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    total_pengeluaran = fields.Float(digits=(6, 0), states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    # komisi_sopir_percentage = fields.Float(digits=(6, 0), tracking=True, states={
    #     'draft': [('readonly', False)],
    #     'done': [('readonly', True)],
    #     'cancel': [('readonly', True)],
    # })

    # komisi_kenek_percentage = fields.Float(digits=(6, 0), tracking=True, states={
    #     'draft': [('readonly', False)],
    #     'done': [('readonly', True)],
    #     'cancel': [('readonly', True)],
    # })

    total_ongkos = fields.Integer('Total Ongkos', default=90, tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    # expense_count = fields.Integer(compute='_compute_expense_count')
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    vendor_bills_count = fields.Integer(compute='_compute_bills_count')

    def _compute_bills_count(self):
        vendor_bills = self.env['account.move'].search([('nomor_setoran', '=', self.kode_oper_setoran), ('move_type', '=', 'in_invoice')])
        self.vendor_bills_count = len(vendor_bills)

    def _compute_invoice_count(self):
        for record in self.detail_order:
            invoices = self.env['account.move'].search([('nomor_setoran', '=', str(self.kode_oper_setoran)), ('move_type', '=', 'out_invoice')])
            inv_count = len(invoices)
            self.invoice_count = inv_count

    # def _compute_expense_count(self):
    #     expenses = self.env['hr.expense'].search([('reference', '=', self.kode_oper_setoran)])
    #     self.expense_count = len(expenses)

    def action_get_invoice_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [['nomor_setoran', '=', str(self.kode_oper_setoran)], ['move_type', '=', 'out_invoice']],
            'context': {
                'create': False,
                'edit': False,  # Prevent record editing
                'delete': False
            }
        }

    def action_get_expenses_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expenses',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'domain': [('reference', '=', str(self.kode_oper_setoran))],
            'context': {
                'create': False,
                'edit': False,  # Prevent record editing
                'delete': False
            }
        }

    def action_get_vendor_bill_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [['nomor_setoran', '=', str(self.kode_oper_setoran)], ['move_type', '=', 'in_invoice']],
            'context': {
                'create': False,
                'edit': False,  # Prevent record editing
                'delete': False
            }
        }

    def unlink(self):
        if any(record.state not in ('draft', 'cancel') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'Draft' atau 'Cancel'.")

        return super(OperSetoran, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('kode_oper_setoran', 'New') == 'New':
            vals['kode_oper_setoran'] = self.env['ir.sequence'].next_by_code('oper.setoran.sequence') or 'New'
        result = super(OperSetoran, self).create(vals)

        oper_order_detail_list_ids = []
        oper_order_list_ids = []

        kendaraan_orm = str(vals['kendaraan']).replace(" ", "").lower()

        for record in self.env['oper.order'].search([('vendor_pa', '=', vals['vendor_pa']), ('kendaraan_orm','=', kendaraan_orm), ('state', '=', 'confirmed')]):
        ############################## Membuat Dictionary-List Oper Order ###########################
            oper_order_detail_list_ids += record.mapped('oper_order_line.order_pengiriman').ids

            list_oper_order_dict = {
                'oper_order': record.id,
                'vendor_pa': record.vendor_pa.id,
                'kendaraan' : record.kendaraan,
                'jumlah_oper_order' : record.biaya_total,
            }
            oper_order_list_ids.append(list_oper_order_dict)

        ############################## Mengeksekusi Create Record ################################
        for item in oper_order_list_ids:
            self.env['list.oper.order.setoran'].create([{
                'oper_setoran': result.id,
                'oper_order': item['oper_order'],
                'vendor_pa': item['vendor_pa'],
                'kendaraan': item['kendaraan'],
                'jumlah_oper_order': item['jumlah_oper_order'],
            }])

        for record_id in oper_order_detail_list_ids:
            record = self.env['order.pengiriman'].browse(record_id)
            self.env['detail.order.setoran'].create([{
                'oper_setoran': result.id,
                'order_pengiriman' : record.id,
                'tanggal_order' : record.create_date,
                'jenis_order' : record.jenis_order,
                'customer' : record.customer.id,
                'plant' : record.plant if record.plant else None,
                'jumlah' : record.total_ongkos,
            }])

            if record.biaya_pembelian:
                self.env['list.pembelian.setoran'].create([{
                    'oper_setoran': result.id,
                    'order_pengiriman' : record.id,
                    'nominal' : record.total_biaya_pembelian,
                }])

            if record.biaya_fee:
                self.env['biaya.fee.setoran'].create([{
                    'oper_setoran': result.id,
                    'order_pengiriman' : record.id,
                    'nominal' : record.total_biaya_fee,
                }])

        oper_order_model = self.env['oper.order'].search([
            ('vendor_pa', '=', vals.get('vendor_pa', self.vendor_pa.id)),
            ('kendaraan_orm', '=', kendaraan_orm),
            ('state', '=', 'confirmed')
        ])

        if not oper_order_model:
            self.env.user.notify_warning(
                message='Oper Order dengan kriteria Vendor PA serta kendaraan yang Anda pilih tidak ditemukan. Pastikan Oper order ada dan berstatus "Confirmed".',
                sticky=True, title='Oper Setoran ' + str(vals.get('kode_oper_setoran')) + ' : Detail Oper Order Tidak Ditemukan')
        else:
            pass

        return result

    def write(self, vals):
        if 'kendaraan' in vals or 'vendor_pa' in vals:

            if 'kendaraan' in vals and vals['kendaraan']:
                kendaraan_orm = str(vals['kendaraan']).replace(" ", "").lower()
            elif self.kendaraan:
                kendaraan_orm = str(self.kendaraan).replace(" ", "").lower()

            ############################## Rewrite Dictionary-List Detail Order ###########################

            for record in self.detail_order:
                record.order_pengiriman.nomor_surat_jalan = None
                record.order_pengiriman.tanggal_uang_jalan = None
                record.unlink()

            for record in self.list_oper_order:
                record.unlink()

            for record in self.list_pembelian_setoran:
                record.unlink()

            for record in self.biaya_fee_setoran:
                record.unlink()

            oper_order_detail_list_ids = []
            oper_order_list_ids = []

            for record in self.env['oper.order'].search([
                ('state', '=', 'confirmed'),
                ('vendor_pa', '=', vals.get('vendor_pa', self.vendor_pa.id)),
                ('kendaraan_orm', '=', kendaraan_orm),
            ]):

            ############################## Membuat Dictionary-List Oper Order ###########################
                oper_order_detail_list_ids.append(int(record.mapped('oper_order_line.order_pengiriman')))

                list_oper_order_dict = {
                    'oper_order': record.id,
                    'vendor_pa': record.vendor_pa.id,
                    'kendaraan': record.kendaraan,
                    'jumlah_oper_order': record.biaya_total,
                }
                oper_order_list_ids.append(list_oper_order_dict)

            ############################## Mengeksekusi Create Record ################################
            for item in oper_order_list_ids:
                self.env['list.oper.order.setoran'].create([{
                    'oper_setoran': self.id,
                    'oper_order': item['oper_order'],
                    'vendor_pa': item['vendor_pa'],
                    'kendaraan': item['kendaraan'],
                    'jumlah_oper_order': item['jumlah_oper_order'],
                }])

            for record in self.env['order.pengiriman'].search([('id', 'in', oper_order_detail_list_ids)]):
                self.env['detail.order.setoran'].create([{
                    'oper_setoran': self.id,
                    'order_pengiriman': record.id,
                    'tanggal_order': record.create_date,
                    'jenis_order': record.jenis_order,
                    'customer': record.customer.id,
                    'plant': record.plant if record.plant else None,
                    'jumlah': record.total_ongkos,
                }])

                if record.biaya_pembelian:
                    self.env['list.pembelian.setoran'].create([{
                        'oper_setoran': self.id,
                        'order_pengiriman': record.id,
                        'nominal': record.total_biaya_pembelian,
                    }])

                if record.biaya_fee:
                    self.env['biaya.fee.setoran'].create([{
                        'oper_setoran': self.id,
                        'order_pengiriman': record.id,
                        'nominal': record.total_biaya_fee,
                    }])

            oper_order_model = self.env['oper.order'].search([
                ('vendor_pa', '=', vals.get('vendor_pa', self.vendor_pa.id)),
                ('kendaraan_orm', '=', kendaraan_orm),
                ('state', '=', 'confirmed')
            ])

            if not oper_order_model:
                self.env.user.notify_warning(
                    message='Oper Order dengan kriteria Vendor PA serta kendaraan yang Anda pilih tidak ditemukan. Pastikan Oper order ada dan berstatus "Confirmed".',
                    sticky=True,
                    title='Oper Setoran ' + str(self.kode_oper_setoran) + ' : Detail Oper Order Tidak Ditemukan')
            else:
                pass

        return super(OperSetoran, self).write(vals)

    def validate(self):

        # Cek Detail Order
        if bool(self.detail_order) == False:
            raise ValidationError('Detail Order Belum Terisi!')
        elif bool(self.list_oper_order) == False:
            raise ValidationError('List Oper Order Belum Terisi!')

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.oper.payment',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Create Invoice',
        }

        # def find_external_id(self):
        #     # Mengambil ID Database Produk berdasarkan external ID
        #     external_id = self.env.ref('order_setoran.product_jasa_pengiriman')
        #     product_id = self.env['product.product'].search([('product_tmpl_id', '=', int(external_id))]).id
        #     return product_id

        # tanggal_oper_order = []
        # for rec in self.list_oper_order:
        #     tanggal_oper_order.append(rec.list_oper_order.oper_order.create_date)
        #
        # formatted_dates = [date.strftime('%d/%m/%Y') for date in tanggal_oper_order]
        # formatted_dates_str = ', '.join(formatted_dates)
        #
        #
        #
        # # Write Nomor Surat Jalan
        # for record in self.detail_order:
        #     record.order_pengiriman.write({
        #         'is_sudah_disetor': True,
        #         'state': 'sudah_setor',
        #         'nomor_surat_jalan': record.nomor_surat_jalan or None,
        #         'nomor_tanggal_uang_jalan': record.surat_uang_jalan or None,
        #     })

        # # Perhitungan & pembuatan expenses
        # if self.total_uang_jalan - self.total_pengeluaran < 0:
        #     pass

        # self.state = 'done'

    def cancel(self):
        # Update Order Pengiriman
        for record in self.detail_order:
            record.order_pengiriman.write({
                'is_sudah_disetor': False,
                'state': 'selesai',
                'nomor_surat_jalan': None,
                'tanggal_uang_jalan': None,
            })

        # Cancel Invoice
        for invoices in self.env['account.move'].search([('nomor_setoran', '=', str(self.kode_oper_setoran)), ('move_type', '=', 'out_invoice')]):
            if invoices.state == 'posted':
                raise ValidationError(
                    "Anda tidak dapat membatalkan setoran ini karena invoice sudah lunas.")
            elif invoices.state == 'draft':
                invoices.state = 'cancel'

       # Cancel Vendor Bill
        for vendor_bills in self.env['account.move'].search([('nomor_setoran', '=', self.kode_oper_setoran), ('move_type', '=', 'in_invoice')]):
            if vendor_bills.state == 'posted':
                raise ValidationError(
                    "Anda tidak dapat membatalkan setoran ini karena vendor bill sudah lunas.")
            elif vendor_bills.state == 'draft':
                vendor_bills.state = 'cancel'

        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    # @api.depends('sisa', 'komisi_kenek_percentage')
    # def _compute_komisi_kenek(self):
    #     for record in self:
    #         record.komisi_kenek = (record.komisi_kenek_percentage * record.sisa) / 100

    # @api.depends('sisa', 'komisi_sopir_percentage')
    # def _compute_komisi_sopir(self):
    #     for record in self:
    #         record.komisi_sopir = (record.komisi_sopir_percentage * record.sisa) / 100

    @api.depends('total_jumlah', 'total_oper_order', 'total_list_pembelian', 'total_biaya_fee')
    def _calculate_sisa(self):
        for record in self:
            record.sisa = record.total_jumlah - record.total_oper_order - record.total_list_pembelian - record.total_biaya_fee

    total_ongkos_calculated = fields.Float(digits=(6, 0), compute='_compute_total_ongkos_calculated')
    @api.depends('total_ongkos')
    def _compute_total_ongkos_calculated(self):
        for record in self:
            record.total_ongkos_calculated = (record.total_jumlah * record.total_ongkos)/100

    @api.depends('detail_order.jumlah')
    def _compute_jumlah(self):
        for record in self:
            record.total_jumlah = sum(record.detail_order.mapped('jumlah'))

    @api.depends('detail_order.bayar_dimuka')
    def _compute_total_bayar_dimuka(self):
        for record in self:
            record.total_bayar_dimuka = sum(record.detail_order.mapped('bayar_dimuka'))

    @api.depends('list_oper_order.jumlah_oper_order')
    def _compute_jumlah_oper_order(self):
        for record in self:
            record.total_oper_order = sum(record.list_oper_order.mapped('jumlah_oper_order'))

    @api.depends('list_pembelian_setoran.nominal')
    def _compute_jumlah_list_pembelian(self):
        for record in self:
            record.total_list_pembelian = sum(record.list_pembelian_setoran.mapped('nominal'))

    @api.depends('biaya_fee_setoran.nominal')
    def _compute_total_biaya_fee(self):
        for record in self:
            record.total_biaya_fee = sum(record.biaya_fee_setoran.mapped('nominal'))

    @api.depends('list_pembelian_setoran.nominal')
    def _compute_total_pembelian(self):
        for record in self:
            record.total_pembelian = sum(record.list_pembelian_setoran.mapped('nominal'))

class DetailOrder(models.Model):
    _name = 'detail.order.setoran'
    _description = 'Detail Order'

    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'Nomor Order', )
    tanggal_order = fields.Datetime('Tanggal Order')
    jenis_order = fields.Selection([('do', 'DO'),('regular', 'Regular'),], required=True, tracking=True)
    customer = fields.Many2one('res.partner', 'Customer', required=True, tracking=True)
    plant = fields.Many2one('konfigurasi.plant', 'PLANT', tracking=True)
    nomor_surat_jalan = fields.Char('No Surat Jalan')
    tanggal_surat_jalan = fields.Date('Tanggal Surat Jalan')
    jumlah = fields.Float('Jumlah', digits=(6, 0))
    bayar_dimuka = fields.Float('Bayar Dimuka', digits=(6, 0))

class ListOperOrder(models.Model):
    _name = 'list.oper.order.setoran'
    _description = 'List Oper Order'

    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    oper_order = fields.Many2one('oper.order', 'No. Oper Order')
    vendor_pa = fields.Many2one('res.partner', 'Vendor PA')
    kendaraan = fields.Char('Kendaraan')
    jumlah_oper_order = fields.Float('Nominal', digits=(6, 0))
    tanggal_dibuat = fields.Datetime('Tanggal Dibuat')

class ListPembelian(models.Model):
    _name = 'list.pembelian.setoran'
    _description = 'List Pembelian'

    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'Nomor Order', )
    nominal = fields.Float('Nominal', digits=(6, 0))

class BiayaFee(models.Model):
    _name = 'biaya.fee.setoran'
    _description = 'Biaya Fee'

    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'Nomor Order', )
    nominal = fields.Float('Nominal', digits=(6, 0))
