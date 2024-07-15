from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class OperSetoran(models.Model):
    _name = 'oper.setoran'
    _description = 'Oper Setoran'
    _inherit = ['mail.thread']
    _rec_name = 'kode_oper_setoran'

    kode_oper_setoran = fields.Char(readonly=True, required=True, copy=False, default='New')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    total_jumlah = fields.Float(compute='_compute_jumlah', digits=(6, 0))
    total_bayar_dimuka = fields.Float(compute='_compute_total_bayar_dimuka', digits=(6, 0))
    total_pendapatan = fields.Float(digits=(6, 0))
    total_pembelian = fields.Float(compute='_compute_total_pembelian', digits=(6, 0))
    total_biaya_fee = fields.Float(compute='_compute_total_biaya_fee', digits=(6, 0))
    total_oper_order = fields.Float(compute='_compute_jumlah_oper_order', digits=(6, 0))
    total_list_pembelian = fields.Float(compute='_compute_jumlah_list_pembelian', digits=(6, 0))
    sisa = fields.Float(compute='_calculate_sisa', digits=(6, 0))
    active = fields.Boolean('Archive', default=True, tracking=True)
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    vendor_bills_count = fields.Integer(compute='_compute_bills_count')
    total_ongkos_calculated = fields.Float(digits=(6, 0), compute='_compute_total_ongkos_calculated')

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

    @api.onchange("detail_order")
    def _populate_oper_order(self):
        for i in self:
            order_ids = [order.order_pengiriman.id for order in i.detail_order]
            i.list_oper_order = [(5, 0, 0)]
            i.biaya_fee_setoran = [(5, 0 ,0)]
            if len(order_ids) > 0:
                oper_order_line_ids = self.env['oper.order.line'].search([('order_pengiriman', 'in', order_ids)])
                oper_order_values = []
                biaya_fee_values = []

                ids = []
                for oper_order_line in oper_order_line_ids:
                    if oper_order_line.id not in ids:
                        ids.append(oper_order_line.id)
                        oper_order_values.append({
                            'oper_setoran': i.id,
                            'oper_order': oper_order_line.oper_order.id,
                            'vendor_pa': oper_order_line.oper_order.vendor_pa.id,
                            'kendaraan': oper_order_line.oper_order.kendaraan,
                            'jumlah_oper_order': oper_order_line.oper_order.biaya_total,
                        })
                        biaya_fee_values.append({
                            'oper_setoran': i.id,
                            'order_pengiriman': oper_order_line.order_pengiriman.id,
                            'nominal': oper_order_line.order_pengiriman.total_biaya_fee,
                        })
                if len(oper_order_values) > 0:
                    self.env['list.oper.order.setoran'].create(oper_order_values)
                if len(biaya_fee_values) > 0:
                    self.env['biaya.fee.setoran'].create(biaya_fee_values)

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

    total_ongkos = fields.Integer('Total Ongkos', default=90, tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    def _compute_bills_count(self):
        try:
            vendor_bills = self.env['account.move'].search([
                ('nomor_setoran', '=', self.kode_oper_setoran),
                ('move_type', '=', 'in_invoice'),
                ('company_id', '=', self.env.company.id),
            ])
            self.vendor_bills_count = len(vendor_bills)
        except:
            self.vendor_bills_count = 0

    def _compute_invoice_count(self):
        self.invoice_count = 0

        try:
            for record in self.detail_order:
                invoices = self.env['account.move'].search([
                    ('nomor_setoran', '=', str(self.kode_oper_setoran)),
                    ('move_type', '=', 'out_invoice'),
                    ('company_id', '=', self.env.company.id),
                ])
                inv_count = len(invoices)
                self.invoice_count = inv_count
        except:
            self.invoice_count = 0

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
                'edit': False,
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
                'edit': False,
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
                'edit': False,
                'delete': False
            }
        }

    def action_create_order_pengiriman(self):
        for i in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'order.pengiriman', 
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
            }

    def action_create_oper_order(self):
        for i in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'oper.order', 
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
            }

    def unlink(self):
        if any(record.state not in ('draft', 'cancel') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'Draft' atau 'Cancel'.")

        return super(OperSetoran, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('kode_oper_setoran', 'New') == 'New':
            vals['kode_oper_setoran'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('oper.setoran.sequence') or 'New'
        result = super(OperSetoran, self).create(vals)

        oper_order_detail_list_ids = []
        oper_order_list_ids = []

        kendaraan_orm = str(vals['kendaraan']).replace(" ", "").lower()

        for record in self.env['oper.order'].search([
            ('vendor_pa', '=', vals['vendor_pa']),
            ('kendaraan_orm','=', kendaraan_orm),
            ('state', '=', 'confirmed'),
            ('company_id', '=', self.env.company.id)
        ]):
        ############################## Membuat Dictionary-List Oper Order ###########################
            oper_order_detail_list_ids += record.mapped('oper_order_line.order_pengiriman').ids

            for order_pengiriman_id in oper_order_detail_list_ids:
                order_pengiriman = self.env['order.pengiriman'].browse(order_pengiriman_id)
                order_pengiriman.oper_setoran = result.kode_oper_setoran

            # Meng-assign nomor setoran ke dalam order pengiriman meskipun statusnya masih draft
            # Untuk membantu proses perubahan atau update biaya fee (jika ada)

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
            ('state', '=', 'confirmed'),
            ('company_id', '=', self.env.company.id),
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
                ('company_id', '=', self.env.company.id),
            ]):

            ############################## Membuat Dictionary-List Oper Order ###########################
                oper_order_detail_list_ids += record.mapped('oper_order_line.order_pengiriman').ids

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
                ('state', '=', 'confirmed'),
                ('company_id', '=', self.env.company.id)
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

        # Cek Nomor Surat Jalan & Tanggal
        for order in self.detail_order:
            if order.nomor_surat_jalan == False:
                raise ValidationError('Nomor Surat Jalan belum terisi ' + str(order.order_pengiriman.order_pengiriman_name))

            if order.tanggal_surat_jalan == False:
                raise ValidationError('Tanggal Surat Jalan belum terisi! ' + str(order.order_pengiriman.order_pengiriman_name))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.oper.payment',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Create Invoice',
        }

    def cancel(self):
        # Update Order Pengiriman
        for record in self.detail_order:
            record.order_pengiriman.write({
                'is_sudah_disetor': False,
                'state': 'selesai',
                'nomor_surat_jalan': None,
            })

        # Cancel Invoice
        for invoices in self.env['account.move'].search([
            ('nomor_setoran', '=', str(self.kode_oper_setoran)),
            ('move_type', '=', 'out_invoice'),
            ('company_id', '=', self.env.company.id),
        ]):
                invoices.state = 'cancel'

       # Cancel Vendor Bill
        for vendor_bills in self.env['account.move'].search([
            ('nomor_setoran', '=', self.kode_oper_setoran),
            ('move_type', '=', 'in_invoice'),
            ('company_id', '=', self.env.company.id),
        ]):
            vendor_bills.state = 'cancel'

        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    @api.depends('total_jumlah', 'total_oper_order', 'total_list_pembelian', 'total_biaya_fee')
    def _calculate_sisa(self):
        for record in self:
            record.sisa = record.total_jumlah - record.total_oper_order - record.total_list_pembelian - record.total_biaya_fee

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

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'Nomor Order')
    tanggal_order = fields.Datetime('Tanggal Order')
    jenis_order = fields.Selection([('do', 'DO'),('regular', 'Regular'),], required=True, tracking=True)
    customer = fields.Many2one('res.partner', 'Customer', required=True, tracking=True)
    plant = fields.Many2one('konfigurasi.plant', 'PLANT', tracking=True)
    nomor_surat_jalan = fields.Char('No Surat Jalan')
    tanggal_surat_jalan = fields.Date('Tanggal Surat Jalan')
    jumlah = fields.Float('Jumlah', digits=(6, 0))
    bayar_dimuka = fields.Float('Bayar Dimuka', digits=(6, 0))

    @api.onchange("order_pengiriman")
    def _get_default_values(self):
        for i in self:
            if i.order_pengiriman:
                i.tanggal_order = i.order_pengiriman.create_date
                i.jenis_order = i.order_pengiriman.jenis_order
                i.customer = i.order_pengiriman.customer
                i.plant = i.order_pengiriman.plant
                i.nomor_surat_jalan = i.order_pengiriman.nomor_surat_jalan

class ListOperOrder(models.Model):
    _name = 'list.oper.order.setoran'
    _description = 'List Oper Order'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    oper_order = fields.Many2one('oper.order', 'No. Oper Order')
    vendor_pa = fields.Many2one('res.partner', 'Vendor PA')
    kendaraan = fields.Char('Kendaraan')
    jumlah_oper_order = fields.Float('Nominal', digits=(6, 0))
    tanggal_dibuat = fields.Datetime('Tanggal Dibuat')

class ListPembelian(models.Model):
    _name = 'list.pembelian.setoran'
    _description = 'List Pembelian'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'Nomor Order', )
    nominal = fields.Float('Nominal', digits=(6, 0))

class BiayaFee(models.Model):
    _name = 'biaya.fee.setoran'
    _description = 'Biaya Fee'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    oper_setoran = fields.Many2one('oper.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'Nomor Order', )
    nominal = fields.Float('Nominal', digits=(6, 0))
