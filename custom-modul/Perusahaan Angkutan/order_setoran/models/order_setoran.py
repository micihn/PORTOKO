import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class OrderSetoran(models.Model):
    _name = 'order.setoran'
    _description = 'Order Setoran'
    _inherit = ['mail.thread']
    _rec_name = 'kode_order_setoran'

    kode_order_setoran = fields.Char(readonly=True, required=True, copy=False, default='New')
    total_jumlah = fields.Float('Total', compute='_compute_total', digits=(6, 0))
    total_bayar_dimuka = fields.Float('Bayar Dimuka', compute='_compute_total_bayar_dimuka', digits=(6, 0))
    total_uang_jalan = fields.Float(compute='_compute_total_uang_jalan', digits=(6, 0))
    total_pembelian = fields.Float(compute='_compute_total_pembelian', digits=(6, 0))
    total_biaya_fee = fields.Float(compute='_compute_biaya_fee', digits=(6, 0))
    sisa = fields.Float(compute='_calculate_sisa', digits=(6, 0))
    total_ongkos_calculated = fields.Float(compute='_compute_total_ongkos_calculated', digits=(6, 3))
    komisi_sopir = fields.Float(compute='_compute_komisi_sopir', digits=(6, 3))
    komisi_kenek = fields.Float(compute='_compute_komisi_kenek', digits=(6, 3))
    active = fields.Boolean('Archive', default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    kendaraan = fields.Many2one('fleet.vehicle', 'Kendaraan', tracking=True, required=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    sopir = fields.Many2one('hr.employee', 'Sopir', tracking=True, required=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    kenek = fields.Many2one('hr.employee', 'Kenek', tracking=True, required=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    tanggal_st = fields.Date('Tanggal ST', tracking=True, required=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    keterangan = fields.Text('Keterangan', tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    keterangan_komisi_sopir = fields.Char('Keterangan Komisi Sopir', tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    keterangan_komisi_kenek = fields.Char('Keterangan Komisi Kenek', tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    total_pengeluaran = fields.Float(digits=(6, 0), compute='_compute_total_pengeluaran', store=True, readonly=False, states={
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    total_ongkos = fields.Float('Total Ongkos', default=90, digits=(6, 3), tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    komisi_sopir_percentage = fields.Float(tracking=True, digits=(6, 3), states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    komisi_kenek_percentage = fields.Float(tracking=True, digits=(6, 3), states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    state = fields.Selection([
        ('draft', "Draft"),
        ('done', "Done"),
        ('cancel', "cancel")
    ], default='draft', string="State", index=True, hide=True, tracking=True)

    detail_order = fields.One2many('detail.order', 'order_setoran', states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
    })

    rincian_pengeluaran = fields.One2many('detail.total.pengeluaran', 'order_setoran', states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
    })

    list_uang_jalan = fields.One2many('detail.list.uang.jalan', 'order_setoran', states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
    })

    list_pembelian = fields.One2many('detail.list.pembelian', 'order_setoran', states={
        'draft': [('readonly', False)],
        'done': [('readonly', False)],
    })

    biaya_fee = fields.One2many('detail.biaya.fee', 'order_setoran', states={
        'draft': [('readonly', False)],
        'done': [('readonly', False)],
    })

    expense_count = fields.Integer(compute='_compute_expense_count')
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    vendor_bills_count = fields.Integer(compute='_compute_bills_count')

    def _compute_bills_count(self):
        try:
            vendor_bills = self.env['account.move'].search([('nomor_setoran', '=', self.kode_order_setoran), ('move_type', '=', 'in_invoice')])
            self.vendor_bills_count = len(vendor_bills)
        except:
            self.vendor_bills_count = 0

    def _compute_invoice_count(self):
        for record in self:
            try:
                invoices = self.env['account.move'].search([('nomor_setoran', '=', str(record.kode_order_setoran)), ('move_type', '=', 'out_invoice')])
                inv_count = len(invoices)
                record.invoice_count = inv_count
            except Exception as e:
                print(f"An error occurred: {e}")
                record.invoice_count = 0

    def _compute_expense_count(self):
        try:
            expenses = self.env['hr.expense'].search([('reference', '=', self.kode_order_setoran)])
            self.expense_count = len(expenses)
        except:
            self.expense_count = 0

    def action_get_vendor_bill_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [['nomor_setoran', '=', str(self.kode_order_setoran)], ['move_type', '=', 'in_invoice']],
            'context': {
                'create': False,
                'edit': False,  # Prevent record editing
                'delete': False
            }
        }

    def action_get_invoice_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [['nomor_setoran', '=', str(self.kode_order_setoran)], ['move_type', '=', 'out_invoice']],

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
            'domain': [('reference', '=', str(self.kode_order_setoran))],
            'context': {
                'create': False,
                'edit': False,  # Prevent record editing
                'delete': False
            }
        }

    def unlink(self):
        if any(record.state not in ('draft', 'cancel') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'Draft' atau 'Cancel'.")

        return super(OrderSetoran, self).unlink()

    def validate(self):

        # Cek Detail Order
        if bool(self.detail_order) == False:
            raise ValidationError('Detail Order Belum Terisi!')

        # Cek Total Pengeluaran
        if self.total_pengeluaran == 0:
            raise ValidationError('Total Pengeluaran belum diisi!')

        # Cek Nomor Surat Jalan & Tanggal
        for order in self.detail_order:
            if order.nomor_surat_jalan == False:
                raise ValidationError('Nomor Surat Jalan belum terisi ' + str(order.order_pengiriman.order_pengiriman_name))

            if order.tanggal_surat_jalan == False:
                raise ValidationError('Tanggal Surat Jalan belum terisi! ' + str(order.order_pengiriman.order_pengiriman_name))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.payment',
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
                'nomor_setoran': None,
            })

        # Batalkan Expenses
        for expense in self.env['hr.expense'].search([('reference', '=', self.kode_order_setoran)]):
            expense.state = 'refused'

        # Batalkan Invoice
        for invoice in self.env['account.move'].search([('nomor_setoran', '=', str(self.kode_order_setoran)), ('move_type', '=', 'out_invoice')]):
            invoice.state = 'cancel'

        # Cancel Vendor Bill
        for vendor_bills in self.env['account.move'].search([('nomor_setoran', '=', self.kode_order_setoran), ('move_type', '=', 'in_invoice')]):
            vendor_bills.state = 'cancel'

        # Batalkan journal entry pembuatan advanced pihut (Jika ada)
        if self.state == 'done':
            for record in self.env['account.move'].search([('ref', '=', str(self.kode_order_setoran))]):
                record.button_draft()
                record.button_cancel()

        # This will close uang jalan
        try:
            for line in self.list_uang_jalan:
                line.uang_jalan_name.order_disetor -= 1

                if line.uang_jalan_name.order_disetor != line.uang_jalan_name.lines_count:
                    line.uang_jalan_name.state = 'paid'
        except:
            pass

        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    @api.depends('sisa', 'komisi_kenek_percentage')
    def _compute_komisi_kenek(self):
        for record in self:
            komisi_kenek = (record.komisi_kenek_percentage * record.sisa) / 100
            record.komisi_kenek = round(komisi_kenek / 1000) * 1000

    @api.depends('sisa', 'komisi_sopir_percentage')
    def _compute_komisi_sopir(self):
        for record in self:
            komisi_sopir = (record.komisi_sopir_percentage * record.sisa) / 100
            record.komisi_sopir = round(komisi_sopir / 1000) * 1000

    @api.depends('total_ongkos_calculated', 'total_pengeluaran', 'total_pembelian', 'total_biaya_fee')
    def _calculate_sisa(self):
        for record in self:
            record.sisa = record.total_ongkos_calculated - record.total_pengeluaran - record.total_pembelian - record.total_biaya_fee

    @api.depends('biaya_fee.nominal')
    def _compute_biaya_fee(self):
        for record in self:
            record.total_biaya_fee = sum(record.biaya_fee.mapped('nominal'))

    @api.depends('list_pembelian.nominal')
    def _compute_total_pembelian(self):
        for record in self:
            record.total_pembelian = sum(record.list_pembelian.mapped('nominal'))

    @api.depends('list_uang_jalan.total')
    def _compute_total_uang_jalan(self):
        for record in self:
            record.total_uang_jalan = sum(record.list_uang_jalan.mapped('total'))

    @api.depends('total_ongkos')
    def _compute_total_ongkos_calculated(self):
        for record in self:
            record.total_ongkos_calculated = (record.total_jumlah * record.total_ongkos)/100

    @api.constrains('total_ongkos')
    def _check_total_ongkos(self):
        for record in self:
            if record.total_ongkos > 100:
                raise ValidationError("Maximum allowance for total_ongkos is 100.")

    @api.depends('detail_order.jumlah')
    def _compute_total(self):
        for record in self:
            record.total_jumlah = sum(record.detail_order.mapped('jumlah'))

    @api.depends('detail_order.bayar_dimuka')
    def _compute_total_bayar_dimuka(self):
        for record in self:
            record.total_bayar_dimuka = sum(record.detail_order.mapped('bayar_dimuka'))

    @api.depends('rincian_pengeluaran.nominal_biaya')
    def _compute_total_pengeluaran(self):
        for record in self:
            if record.rincian_pengeluaran.mapped('nominal_biaya'):
                record.total_pengeluaran = sum(record.rincian_pengeluaran.mapped('nominal_biaya'))
            else:
                record.total_pengeluaran = 0

    @api.model
    def create(self, vals):
        ####################### AUTO ASSIGN RECORD NAME ##############################

        if vals.get('kode_order_setoran', 'New') == 'New':
            vals['kode_order_setoran'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('order.setoran.sequence') or 'New'
        result = super(OrderSetoran, self).create(vals)

        # list utama untuk membuat record pada tiap notebook
        detail_order = []
        list_uang_jalan = []
        list_pembelian = []
        list_biaya_fee = []

        # List ini untuk menghindari double input pada setoran
        record_uang_jalan = []

        ############################## Membuat Dictionary-List Detail Order ###########################

        for record in self.env['order.pengiriman'].search([('kendaraan', '=', vals['kendaraan']), ('sopir','=', vals['sopir']), ('kenek','=', vals['kenek']), ('state', '=', 'selesai'), ('company_id', '=', int(self.env.company))]):
            # Meng-assign nomor setoran ke dalam order pengiriman meskipun statusnya masih draft
            # Untuk membantu proses perubahan atau update biaya fee (jika ada)
            record.nomor_setoran = result.kode_order_setoran

            detail_order_dict = {
                'order_pengiriman': record.id,
                'create_date': record.create_date,
                'jenis_order': record.jenis_order,
                'customer_id': record.customer.id,
                'plant': record.plant.id if record.plant else None,
                'total_ongkos': record.total_ongkos_do or record.total_ongkos_reguler
            }
            detail_order.append(detail_order_dict)

        ############################## Membuat Dictionary-List Uang Jalan ###########################

            for uang_jalan in record.uang_jalan:
                if uang_jalan.id not in record_uang_jalan:
                    balance_spend = 0
                    for balance in uang_jalan.balance_history:
                        if str(record.order_pengiriman_name) in balance.keterangan:
                            balance_spend += balance.nominal_close
                        elif balance.keterangan == 'Penggunaan Saldo Uang Jalan Untuk Seluruh Order Pengiriman':
                            balance_spend = balance.nominal_close

                    list_uang_jalan_dict = {
                        'tanggal': uang_jalan.create_date,
                        'uang_jalan_name': uang_jalan.id,
                        'total': balance_spend * -1,
                        'keterangan': uang_jalan.keterangan,
                    }
                    list_uang_jalan.append(list_uang_jalan_dict)
                    record_uang_jalan.append(int(uang_jalan.id))

        ############################## Membuat Dictionary-List Pembelian ###########################

            if record.biaya_pembelian:
                for item in record.biaya_pembelian:
                    detail_list_pembelian_dict = {
                        'order_pengiriman': item.order_pengiriman.id,
                        'supplier': item.supplier.id,
                        'nama_barang': item.nama_barang,
                        'ukuran': item.ukuran,
                        'nominal': item.nominal,
                    }

                    list_pembelian.append(detail_list_pembelian_dict)

        ############################## Membuat Dictionary-List Fee ################################

            if record.biaya_fee:
                for item in record.biaya_fee:
                    detail_list_biaya_fee_dict = {
                        'order_pengiriman': item.order_pengiriman.id,
                        'fee_contact': item.fee_contact.id,
                        'nominal': item.nominal,
                    }

                    list_biaya_fee.append(detail_list_biaya_fee_dict)

        ############################## Mengeksekusi Create Record ################################

        # Membuat detail order
        for item in detail_order:
            self.env['detail.order'].create([{
                'company_id': self.env.company.id,
                'order_setoran': result.id,
                'order_pengiriman': item['order_pengiriman'],
                'tanggal_order': item['create_date'],
                'jenis_order': item['jenis_order'],
                'customer': item['customer_id'],
                'plant': item['plant'],
                'jumlah': item['total_ongkos'],
            }])

        # Membuat detail list uang jalan
        for item in list_uang_jalan:
            self.env['detail.list.uang.jalan'].create([{
                'company_id': self.env.company.id,
                'order_setoran': result.id,
                'tanggal': item['tanggal'],
                'uang_jalan_name': item['uang_jalan_name'],
                'total': item['total'],
                'keterangan': item['keterangan'],
            }])

        # Membuat list pembelian
        for item in list_pembelian:
            self.env['detail.list.pembelian'].create([{
                'company_id': self.env.company.id,
                'order_setoran': result.id,
                'order_pengiriman': item['order_pengiriman'],
                'supplier': item['supplier'],
                'nama_barang': item['nama_barang'],
                'ukuran': item['ukuran'],
                'nominal': item['nominal'],
            }])

        # Membuat list biaya fee
        for item in list_biaya_fee:
            self.env['detail.biaya.fee'].create([{
                'company_id': self.env.company.id,
                'order_setoran': result.id,
                'order_pengiriman': item['order_pengiriman'],
                'fee_contact': item['fee_contact'],
                'nominal': item['nominal'],
            }])

        order_pengiriman_model = self.env['order.pengiriman'].search([
            ('kendaraan', '=', vals.get('kendaraan', self.kendaraan.id)),
            ('sopir', '=', vals.get('sopir', self.sopir.id)),
            ('kenek', '=', vals.get('kenek', self.kenek.id)),
            ('state', '=', 'selesai'),
            ('company_id', '=', int(self.env.company.id))
        ])

        if not order_pengiriman_model:
            self.env.user.notify_warning(message='Order pengiriman dengan kriteria kendaraan, sopir, dan kenek yang Anda pilih tidak ditemukan. Pastikan Order Pengiriman ada dan berstatus "Selesai".', sticky=True, title='Setoran ' + str(vals.get('kode_order_setoran')) + ' : Detail Order Tidak Ditemukan')
        else:
            pass

        return result

    def write(self, vals):
        if 'kendaraan' in vals or 'sopir' in vals or 'kenek' in vals:

            ############################## Rewrite Dictionary-List Detail Order ###########################

            for record in self.detail_order:
                record.order_pengiriman.nomor_surat_jalan = None
                record.unlink()

            for record in self.list_uang_jalan:
                record.unlink()

            for record in self.list_pembelian:
                record.unlink()

            for record in self.biaya_fee:
                record.unlink()

            # list utama untuk membuat record pada tiap notebook
            detail_order = []
            list_uang_jalan = []
            list_pembelian = []
            list_biaya_fee = []

            # List ini untuk menghindari double input pada setoran
            record_uang_jalan = []

            order_pengiriman_model = self.env['order.pengiriman'].search([
                ('kendaraan', '=', vals.get('kendaraan', self.kendaraan.id)),
                ('sopir', '=', vals.get('sopir', self.sopir.id)),
                ('kenek', '=', vals.get('kenek', self.kenek.id)),
                ('state', '=', 'selesai'),
                ('company_id', '=', int(self.env.company.id))
            ])

            if not order_pengiriman_model:
                self.env.user.notify_warning(
                    message='Order pengiriman dengan kriteria kendaraan, sopir, dan kenek yang Anda pilih tidak ditemukan. Pastikan Order Pengiriman ada dan berstatus "Selesai".', sticky=True, title='Setoran ' + str(self.kode_order_setoran) + ' : Detail Order Tidak Ditemukan')
            else:
                pass

            for record in order_pengiriman_model:
                detail_order_dict = {
                    'order_pengiriman': record.id,
                    'create_date': record.create_date,
                    'jenis_order': record.jenis_order,
                    'customer_id': record.customer.id,
                    'plant': record.plant.id if record.plant else None,
                    'total_ongkos': record.total_ongkos_do or record.total_ongkos_reguler
                }
                detail_order.append(detail_order_dict)

            ############################## Rewrite Dictionary-List List Uang Jalan ###########################

                for uang_jalan in record.uang_jalan:
                    if uang_jalan.id not in record_uang_jalan:
                        list_uang_jalan_dict = {
                            'tanggal': uang_jalan.create_date,
                            'uang_jalan_name': uang_jalan.id,
                            'total': uang_jalan.total,
                            'keterangan': uang_jalan.keterangan,
                        }
                        list_uang_jalan.append(list_uang_jalan_dict)
                        record_uang_jalan.append(int(uang_jalan.id))

            ############################## Rewrite Dictionary-List List Pembelian ###########################

                if record.biaya_pembelian:
                    for item in record.biaya_pembelian:
                        detail_list_pembelian_dict = {
                            'order_pengiriman': record.id,
                            'supplier': item.supplier.id,
                            'nama_barang': item.nama_barang,
                            'ukuran': item.ukuran,
                            'nominal': item.nominal,
                        }

                        list_pembelian.append(detail_list_pembelian_dict)

            ############################## Rewrite Dictionary-List Biaya Fee ###########################

                # membuat list pembelian
                if record.biaya_fee:
                    for item in record.biaya_fee:
                        detail_list_biaya_fee_dict = {
                            'order_pengiriman': record.id,
                            'fee_contact': item.fee_contact.id,
                            'nominal': item.nominal,
                        }
                        list_biaya_fee.append(detail_list_biaya_fee_dict)

            ############################## Mengeksekusi WriteRecord ################################

            for record in detail_order:
                self.env['detail.order'].create([{
                    'company_id': self.env.company.id,
                    'order_setoran': self.id,
                    'order_pengiriman': record['order_pengiriman'],
                    'tanggal_order': record['create_date'],
                    'jenis_order': record['jenis_order'],
                    'customer': record['customer_id'],
                    'plant': record['plant'],
                    'jumlah': record['total_ongkos'],
                }])

            for record in list_uang_jalan:
                self.env['detail.list.uang.jalan'].create([{
                    'company_id': self.env.company.id,
                    'order_setoran': self.id,
                    'tanggal': record['tanggal'],
                    'uang_jalan_name': record['uang_jalan_name'],
                    'total': record['total'],
                    'keterangan': record['keterangan'],
            }])

            for record in list_pembelian:
                self.env['detail.list.pembelian'].create([{
                    'company_id': self.env.company.id,
                    'order_setoran': self.id,
                    'order_pengiriman': record['order_pengiriman'],
                    'supplier': record['supplier'],
                    'nama_barang': record['nama_barang'],
                    'ukuran': record['ukuran'],
                    'nominal': record['nominal'],
                }])

            for record in list_biaya_fee:
                self.env['detail.biaya.fee'].create([{
                    'company_id': self.env.company.id,
                    'order_setoran': self.id,
                    'order_pengiriman': record['order_pengiriman'],
                    'fee_contact': record['fee_contact'],
                    'nominal': record['nominal'],
                }])

        res = super(OrderSetoran, self).write(vals)

        # Cek apakah ada penambahan atau perubahan biaya_fee
        if 'biaya_fee' in vals:
            biaya_fee_list_before_updated = []
            # Rewriting Biaya Fee di dalam order setoran
            for record in self.biaya_fee:
                biaya_fee_before_update_dict = {
                    'order_setoran': self.id,
                    'order_pengiriman': record.order_pengiriman.id,
                    'fee_contact': record.fee_contact.id,
                    'nominal': record.nominal,
                }

                biaya_fee_list_before_updated.append(biaya_fee_before_update_dict)

                record.unlink()

            for item in biaya_fee_list_before_updated:
                self.env['detail.biaya.fee'].create({
                    'company_id': self.env.company.id,
                    'order_setoran': self.id,
                    'order_pengiriman': item['order_pengiriman'],
                    'fee_contact': item['fee_contact'],
                    'nominal': item['nominal'],
                })

            # Rewriting Biaya Fee di order pengiriman
            biaya_fee_order_pengiriman = []
            for item in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_fee:
                fee_dict = {
                    'order_pengiriman': item.order_pengiriman.id,
                    'fee_contact': item.fee_contact.id,
                    'nominal': item.nominal,
                }

                biaya_fee_order_pengiriman.append(fee_dict)

            for record in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_fee:
                record.unlink()

            for item in biaya_fee_list_before_updated:
                self.env['biaya.fee'].create({
                    'company_id': self.env.company.id,
                    'order_pengiriman': item['order_pengiriman'],
                    'fee_contact': item['fee_contact'],
                    'nominal': item['nominal'],
                })

        # Cek apakah ada penambahan atau perubahan List Pembelian
        if 'list_pembelian' in vals:
            list_pembelian_before_updated = []
            # Rewriting List Pembelian di dalam order setoran
            for record in self.list_pembelian:
                list_pembelian_before_update_dict = {
                    'order_setoran': self.id,
                    'order_pengiriman': record.order_pengiriman.id,
                    'supplier': record.supplier.id,
                    'nama_barang': record.nama_barang,
                    'nominal': record.nominal,
                }

                list_pembelian_before_updated.append(list_pembelian_before_update_dict)

                record.unlink()

            for item in list_pembelian_before_updated:
                self.env['detail.list.pembelian'].create({
                    'company_id': self.env.company.id,
                    'order_setoran': self.id,
                    'order_pengiriman': item['order_pengiriman'],
                    'supplier': item['supplier'],
                    'nama_barang': item['nama_barang'],
                    'nominal': item['nominal'],
                })

            # Rewriting Biaya Fee di order pengiriman
            list_pembelian_order_pengiriman = []
            for item in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_pembelian:
                list_pembelian_dict = {
                    'order_pengiriman': item.order_pengiriman.id,
                    'supplier': item.supplier.id,
                    'nama_barang': item.nama_barang,
                    'nominal': item.nominal,
                }

                list_pembelian_order_pengiriman.append(list_pembelian_dict)

            for record in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_pembelian:
                record.unlink()

            for item in list_pembelian_before_updated:
                self.env['biaya.pembelian'].create({
                    'company_id': self.env.company.id,
                    'order_pengiriman': item['order_pengiriman'],
                    'supplier': item['supplier'],
                    'nama_barang': item['nama_barang'],
                    'nominal': item['nominal'],
                })

        return res

class DetailOrder(models.Model):
    _name = 'detail.order'
    _description = 'Detail Order'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_setoran = fields.Many2one('order.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
    tanggal_order = fields.Datetime('Tanggal Order')
    customer = fields.Many2one('res.partner', 'Customer', required=True, tracking=True)
    plant = fields.Many2one('konfigurasi.plant', 'PLANT', tracking=True)
    nomor_surat_jalan = fields.Char('No Surat Jalan')
    tanggal_surat_jalan = fields.Date('Tanggal Surat Jalan')
    jumlah = fields.Float('Jumlah', digits=(6, 0))
    bayar_dimuka = fields.Float('Bayar Dimuka', digits=(6, 0))
    jenis_order = fields.Selection([
        ('do', 'DO'),
        ('regular', 'Regular'),
    ], required=True, tracking=True)

    @api.constrains('bayar_dimuka', 'jumlah')
    def _check_bayar_dimuka(self):
        for record in self:
            if record.bayar_dimuka > record.jumlah:
                raise ValidationError('Nominal bayar dimuka lebih besar daripada nominal yang ditagihkan (' +(record.order_pengiriman.order_pengiriman_name) + ').' )

class ListUangJalan(models.Model):
    _name = 'detail.list.uang.jalan'
    _description = 'List Uang Jalan'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_setoran = fields.Many2one('order.setoran', invisible=True)
    tanggal = fields.Date('Tanggal')
    uang_jalan_name = fields.Many2one('uang.jalan', 'No Uang Jalan')
    total = fields.Float('Total', digits=(6, 0))
    keterangan = fields.Text('Keterangan')

class ListPembelian(models.Model):
    _name = 'detail.list.pembelian'
    _description = 'List Pembelian'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_setoran = fields.Many2one('order.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
    supplier = fields.Many2one('res.partner', 'Supplier')
    nama_barang = fields.Char('Nama')
    ukuran = fields.Text('Ukuran')
    nominal = fields.Float('Biaya', digits=(6, 0))

class BiayaFee(models.Model):
    _name = 'detail.biaya.fee'
    _description = 'Biaya Fee'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_setoran = fields.Many2one('order.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
    fee_contact = fields.Many2one('res.partner', 'Nama')
    nominal = fields.Float('Nominal', digits=(6, 0))

class AccountMoveInvoice(models.Model):
    _inherit = 'account.move'

    nomor_setoran = fields.Char('No. Setoran')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

class DetailTotalPengeluaran(models.Model):
    _name = 'detail.total.pengeluaran'
    _description = 'Detail Total Pengeluaran'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_setoran = fields.Many2one('order.setoran', invisible=True)
    rincian_biaya = fields.Char('Rincian Biaya')
    nominal_biaya = fields.Float('Nominal Biaya', digits=(6, 0))