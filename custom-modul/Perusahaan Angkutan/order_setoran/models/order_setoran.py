import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class OrderSetoran(models.Model):
    _name = 'order.setoran'
    _description = 'Order Setoran'
    _inherit = ['mail.thread']
    _rec_name = 'kode_order_setoran'

    kode_order_setoran = fields.Char(readonly=True, required=True, copy=False, string="No. Setoran", default='New')
    total_jumlah = fields.Float('Total', compute='_compute_total', digits=(6, 0))
    total_bayar_dimuka = fields.Float('Bayar Dimuka', compute='_compute_total_bayar_dimuka', digits=(6, 0))
    total_uang_jalan = fields.Float(compute='_compute_total_uang_jalan', digits=(6, 0))
    total_pembelian = fields.Float(compute='_compute_total_pembelian', digits=(6, 0))
    total_biaya_fee = fields.Float(compute='_compute_biaya_fee', digits=(6, 0))
    sisa = fields.Float(compute='_calculate_sisa', digits=(6, 0))
    total_ongkos_calculated = fields.Float(compute='_compute_total_ongkos_calculated', digits=(6, 0))
    komisi_sopir = fields.Float(compute='_compute_komisi_sopir', digits=(6, 0))
    komisi_kenek = fields.Float(compute='_compute_komisi_kenek', digits=(6, 0))
    active = fields.Boolean('Archive', default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    fetch_order_automatic = fields.Boolean()

    kendaraan = fields.Many2one('fleet.vehicle', 'No. Truk', tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    sopir = fields.Many2one('hr.employee', 'Sopir', tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    kenek = fields.Many2one('hr.employee', 'Kenek', tracking=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    class HrEmployee(models.Model):
        _inherit = 'hr.employee'

        @api.model
        def name_search(self, name='', args=None, operator='ilike', limit=100):
            args = args or []
            domain = []
            if name:
                domain = ['|', ('name', operator, name), ('identification_id', operator, name)]
            employees = self.search(domain + args, limit=limit)
            return employees.name_get()

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('identification_id', operator, name)]
        employees = self.search(domain + args, limit=limit)
        return employees.name_get()


    tanggal_st = fields.Date('Tgl. Setor', tracking=True, default=fields.Date.today(), required=True, states={
        'draft': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    tanggal_kasbon_start = fields.Date('Tgl. Kasbon (Start)', tracking=True, required=True, states={
        'draft': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    })

    tanggal_kasbon_finish = fields.Date('Tgl. Kasbon (Finish)', tracking=True, required=True, states={
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

    list_pembelian = fields.Many2many('biaya.pembelian')
    biaya_fee = fields.Many2many('biaya.fee')

    # list_pembelian = fields.One2many('detail.list.pembelian', 'order_setoran', states={
    #     'draft': [('readonly', False)],
    #     'done': [('readonly', False)],
    # })

    # biaya_fee = fields.One2many('detail.biaya.fee', 'order_setoran', states={
    #     'draft': [('readonly', False)],
    #     'done': [('readonly', False)],
    # })

    # relatable_uang_jalan = fields.Many2many('uang.jalan', compute="_compute_total_uang_jalan", string='No. Uang Jalan', copy=False)

    # @api.depends('detail_order.order_pengiriman')
    # def compute_relatable_uang_jalan(self):
    #     for rec in self:
    #         list_uang_jalan = []
    #         for detail in rec.detail_order:  # Assuming detail_order is a One2many or Many2many field
    #             if detail.order_pengiriman:
    #                 for uj in detail.order_pengiriman.uang_jalan:
    #                     list_uang_jalan.append(uj.id)  # Using (4, id) to add records to Many2many field

    #         rec.relatable_uang_jalan = [(6, 0, list_uang_jalan)]  # Clear existing records, then add new ones

    @api.onchange('kendaraan', 'tanggal_kasbon_start', 'tanggal_kasbon_finish')
    def set_driver_and_kenek(self):
        if bool(self.kendaraan) and bool(self.tanggal_kasbon_start) and bool(self.tanggal_kasbon_finish):
            self.sopir = False
            self.kenek = False
            self.list_uang_jalan = [(5, 0, 0)]

            list_uang_jalan = self.env['uang.jalan'].sudo().search([
                ('kendaraan', '=', self.kendaraan.id),
                ('create_date', '>=', self.tanggal_kasbon_start),
                ('create_date', '<=', self.tanggal_kasbon_finish),
                ('state', 'in', ['paid']),
            ])

            if bool(list_uang_jalan):
                for uang_jalan in list_uang_jalan:
                    if bool(self.sopir) == False:
                        self.sopir = uang_jalan.sopir.id

                    if bool(self.kenek) == False:
                        self.kenek = uang_jalan.kenek.id

                    self.list_uang_jalan.create({
                        'order_setoran': self.id,
                        'uang_jalan_name': uang_jalan.id,
                        'tanggal': uang_jalan.create_date.date() if uang_jalan.create_date else False,
                    })
            else:
                self.list_uang_jalan.unlink()

    # relatable_list_pembelian = fields.Many2many('biaya.pembelian', compute="compute_relatable_biaya_pembelian", copy=False)
    # @api.depends('detail_order.order_pengiriman')
    # def compute_relatable_biaya_pembelian(self):
    #     for rec in self:
    #         list_biaya_pembelian = []
    #         for detail in rec.detail_order:  # Assuming detail_order is a One2many or Many2many field
    #             if detail.order_pengiriman:
    #                 for pembelian in detail.order_pengiriman.biaya_pembelian:
    #                     list_biaya_pembelian.append((4, pembelian.id))  # Using (4, id) to add records to Many2many field
    #
    #         rec.relatable_list_pembelian = [(5, 0, 0)] + list_biaya_pembelian  # Clear existing records, then add new ones

    # relatable_list_pembelian = fields.Many2many('biaya.pembelian', compute="compute_relatable_biaya_pembelian", copy=False)
    # @api.depends('detail_order.order_pengiriman')
    # def compute_relatable_biaya_pembelian(self):
    #     for rec in self:
    #         list_biaya_pembelian = []
    #         for detail in rec.detail_order:  # Assuming detail_order is a One2many or Many2many field
    #             if detail.order_pengiriman:
    #                 for pembelian in detail.order_pengiriman.biaya_pembelian:
    #                     list_biaya_pembelian.append((4, pembelian.id))  # Using (4, id) to add records to Many2many field
    #
    #         rec.relatable_list_pembelian = [(5, 0, 0)] + list_biaya_pembelian  # Clear existing records, then add new ones

    # relatable_biaya_fee = fields.Many2many('biaya.fee', copy=False)
    # @api.depends('detail_order.order_pengiriman')
    # def compute_relatable_biaya_fee(self):
    #     for rec in self:
    #         list_biaya_fee = []
    #         for detail in rec.detail_order:  # Assuming detail_order is a One2many or Many2many field
    #             if detail.order_pengiriman:
    #                 for biaya_fee in detail.order_pengiriman.biaya_fee:
    #                     list_biaya_fee.append((4, biaya_fee.id))  # Using (4, id) to add records to Many2many field
    #
    #         rec.relatable_biaya_fee = [(5, 0, 0)] + list_biaya_fee  # Clear existing records, then add new ones

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

    # def action_get_expenses_view(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Expenses',
    #         'view_mode': 'tree,form',
    #         'res_model': 'hr.expense',
    #         'domain': [('reference', '=', str(self.kode_order_setoran))],
    #         'context': {
    #             'create': False,
    #             'edit': False,  # Prevent record editing
    #             'delete': False
    #         }
    #     }

    def unlink(self):
        if any(record.state not in ('draft', 'cancel') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'Draft' atau 'Cancel'.")

        return super(OrderSetoran, self).unlink()

    def validate(self):

        # Cek Kendaraan
        if bool(self.kendaraan) == False:
            raise ValidationError('Kendaraan Belum Terisi!')

        if bool(self.sopir) == False:
            raise ValidationError('Sopir Belum Terisi!')

        if bool(self.kenek) == False:
            raise ValidationError('Kenek Belum Terisi!')

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

        for uj in self.list_uang_jalan:
            uj.uang_jalan_name.state = 'to_submit'

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
        total = 0
        for record in self.list_uang_jalan:
            total += record.total

        self.total_uang_jalan = total

        # for record in self:
        #     list_uang_jalan = []
        #     total_uj = 0
        #     for detail in record.detail_order:  # Assuming detail_order is a One2many or Many2many field
        #         if detail.order_pengiriman:
        #             for uj in detail.order_pengiriman.uang_jalan:
        #                 list_uang_jalan.append(uj.id)  # Using (4, id) to add records to Many2many field
        #                 total_uj += uj.total
        #
        #     record.relatable_uang_jalan = [(6, 0, list_uang_jalan)]  # Clear existing records, then add new ones
        #     record.total_uang_jalan = total_uj

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

    # def ambil_order_pengiriman(self):
    #     if bool(self.kendaraan) == False:
    #         raise ValidationError('Kendaraan Belum Diisi!')
    #
    #     if bool(self.sopir) == False:
    #         raise ValidationError('Sopir Belum Diisi!')
    #
    #     if bool(self.kenek) == False:
    #         raise ValidationError('Sopir Belum Diisi!')
    #
    #     self.fetch_order_automatic = True
    #
    #     # list utama untuk membuat record pada tiap notebook
    #     detail_order = []
    #     # list_uang_jalan = []
    #     # list_pembelian = []
    #     # list_biaya_fee = []
    #     # record_uang_jalan = [] # List untuk menghindari double input pada setoran
    #
    #     for record in self.env['order.pengiriman'].search([('kendaraan', '=', self.kendaraan.id), ('sopir','=', self.sopir.id), ('kenek','=', self.kenek.id), ('state', '=', 'selesai'), ('company_id', '=', int(self.env.company))]):
    #         # Untuk membantu proses perubahan atau update biaya fee (jika ada)
    #         record.nomor_setoran = self.kode_order_setoran
    #
    #         # Fase 1 : Membuat Dictionary List
    #         # Membuat Dictionary-List Detail Order
    #         detail_order_dict = {
    #             'order_pengiriman': record.id,
    #             'create_date': record.create_date,
    #             'jenis_order': record.jenis_order,
    #             'customer_id': record.customer.id,
    #             'plant': record.plant.id if record.plant else None,
    #             'total_ongkos': record.total_ongkos_do or record.total_ongkos_reguler
    #         }
    #         detail_order.append(detail_order_dict)
    #
    #         # # Membuat Dictionary-List Uang Jalan
    #         # for uang_jalan in record.uang_jalan:
    #         #     if uang_jalan.id not in record_uang_jalan:
    #         #         list_uang_jalan_dict = {
    #         #             'tanggal': uang_jalan.create_date,
    #         #             'uang_jalan_name': uang_jalan.id,
    #         #             'total': uang_jalan.total,
    #         #             'keterangan': uang_jalan.keterangan,
    #         #         }
    #         #         list_uang_jalan.append(list_uang_jalan_dict)
    #         #         record_uang_jalan.append(int(uang_jalan.id))
    #
    #         # # Membuat Dictionary-List Pembelian
    #         # if record.biaya_pembelian:
    #         #     for item in record.biaya_pembelian:
    #         #         detail_list_pembelian_dict = {
    #         #             'order_pengiriman': item.order_pengiriman.id,
    #         #             'supplier': item.supplier.id,
    #         #             'nama_barang': item.nama_barang,
    #         #             'ukuran': item.ukuran,
    #         #             'nominal': item.nominal,
    #         #         }
    #         #
    #         #         list_pembelian.append(detail_list_pembelian_dict)
    #
    #         # Membuat Dictionary-List Fee
    #         # if record.biaya_fee:
    #         #     for item in record.biaya_fee:
    #         #         detail_list_biaya_fee_dict = {
    #         #             'order_pengiriman': item.order_pengiriman.id,
    #         #             'fee_contact': item.fee_contact.id,
    #         #             'nominal': item.nominal,
    #         #         }
    #         #
    #         #         list_biaya_fee.append(detail_list_biaya_fee_dict)
    #
    #         # Membuat detail list uang jalan
    #         # for item in list_uang_jalan:
    #         #     self.env['detail.list.uang.jalan'].create([{
    #         #         'company_id': self.env.company.id,
    #         #         'order_setoran': self.id,
    #         #         'tanggal': item['tanggal'],
    #         #         'uang_jalan_name': item['uang_jalan_name'],
    #         #         'total': item['total'],
    #         #         'keterangan': item['keterangan'],
    #         #     }])
    #
    #         # # Membuat list pembelian
    #         # for item in list_pembelian:
    #         #     self.env['detail.list.pembelian'].create([{
    #         #         'company_id': self.env.company.id,
    #         #         'order_setoran': self.id,
    #         #         'order_pengiriman': item['order_pengiriman'],
    #         #         'supplier': item['supplier'],
    #         #         'nama_barang': item['nama_barang'],
    #         #         'ukuran': item['ukuran'],
    #         #         'nominal': item['nominal'],
    #         #     }])
    #
    #         # Membuat list biaya fee
    #         # for item in list_biaya_fee:
    #         #     self.env['detail.biaya.fee'].create([{
    #         #         'company_id': self.env.company.id,
    #         #         'order_setoran': self.id,
    #         #         'order_pengiriman': item['order_pengiriman'],
    #         #         'fee_contact': item['fee_contact'],
    #         #         'nominal': item['nominal'],
    #         #     }])
    #
    #         order_pengiriman_model = self.env['order.pengiriman'].search([
    #             ('kendaraan', '=', self.kendaraan.id),
    #             ('sopir', '=', self.sopir.id),
    #             ('kenek', '=', self.kenek.id),
    #             ('state', '=', 'selesai'),
    #             ('company_id', '=', int(self.env.company.id))
    #         ])
    #
    #         if not order_pengiriman_model:
    #             self.env.user.notify_warning(
    #                 message='Order pengiriman dengan kriteria kendaraan, sopir, dan kenek yang Anda pilih tidak ditemukan. Pastikan Order Pengiriman ada dan berstatus "Selesai".',
    #                 sticky=True,
    #                 title='Setoran ' + str(self.kode_order_setoran) + ' : Detail Order Tidak Ditemukan')
    #         else:
    #             pass
    #
    #     # Fase 2 : Duplicate Order Clean Up
    #     unique_list = []
    #     seen_ids = set()
    #     for item in detail_order:
    #         order_id = item['order_pengiriman']
    #         if order_id not in seen_ids:
    #             unique_list.append(item)
    #             seen_ids.add(order_id)
    #
    #     # Fase 3 : Mengeksekusi Create Record
    #     # Membuat detail order
    #     for item in unique_list:
    #         self.env['detail.order'].create([{
    #             'company_id': self.env.company.id,
    #             'order_setoran': self.id,
    #             'order_pengiriman': item['order_pengiriman'],
    #             'tanggal_order': item['create_date'],
    #             'jenis_order': item['jenis_order'],
    #             'customer': item['customer_id'],
    #             'plant': item['plant'],
    #             'jumlah': item['total_ongkos'],
    #         }])

    @api.model
    def create(self, vals):
        # Auto Assign record name
        if vals.get('kode_order_setoran', 'New') == 'New':
            vals['kode_order_setoran'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('order.setoran.sequence') or 'New'
        result = super(OrderSetoran, self).create(vals)

        # setoran = self.env['order.setoran'].search([('id', '=', result.id)])
        # list_uang_jalan = []
        # for order in setoran.detail_order:
            # # Buat Pembelian
            # for pembelian in order.order_pengiriman.biaya_pembelian:
            #     setoran.list_pembelian.create({
            #         'order_pengiriman': order.order_pengiriman.id,
            #         'order_setoran': result.id,
            #         'supplier': pembelian.supplier.id,
            #         'nama_barang': pembelian.nama_barang,
            #         'ukuran': pembelian.ukuran,
            #         'nominal': pembelian.nominal,
            #     })

            # Buat Biaya Fee
            # for biaya_fee in order.order_pengiriman.biaya_fee:
            #     setoran.biaya_fee.create({
            #         'order_pengiriman': order.order_pengiriman.id,
            #         'order_setoran': result.id,
            #         'fee_contact': biaya_fee.fee_contact.id,
            #         'nominal': biaya_fee.nominal,
            #     })

            # # Appending Uang Jalan
            # for uang_jalan in order.order_pengiriman.uang_jalan:
            #     list_uang_jalan.append({
            #         'tanggal_uang_jalan': uang_jalan.create_date,
            #         'uang_jalan_id': uang_jalan.id,
            #         'total': uang_jalan.total,
            #         'keterangan': uang_jalan.keterangan,
            #         'order_id': order.order_pengiriman.id,
            #     })

        # # Remove duplicate uang jalan
        # unique_list = []
        # seen_ids = set()
        # for item in list_uang_jalan:
        #     uang_jalan_id = item['uang_jalan_id']
        #     if uang_jalan_id not in seen_ids:
        #         unique_list.append(item)
        #         seen_ids.add(uang_jalan_id)

        # # Buat Uang Jalan
        # for uj in unique_list:
        #     self.list_uang_jalan.create({
        #         'company_id': self.env.company.id,
        #         'order_setoran': setoran.id,
        #         'order_pengiriman': uj['order_id'],
        #         'tanggal': uj['tanggal_uang_jalan'],
        #         'uang_jalan_name': uj['uang_jalan_id'],
        #         'total': uj['total'],
        #         'keterangan': uj['keterangan'],
        #     })


        ### START
        # # list utama untuk membuat record pada tiap notebook
        # detail_order = []
        # list_uang_jalan = []
        # list_pembelian = []
        # list_biaya_fee = []
        #
        #
        # record_uang_jalan = []
        #
        # ############################## Membuat Dictionary-List Detail Order ###########################
        #
        # for record in self.env['order.pengiriman'].search([('kendaraan', '=', vals['kendaraan']), ('sopir','=', vals['sopir']), ('kenek','=', vals['kenek']), ('state', '=', 'selesai'), ('company_id', '=', int(self.env.company))]):
        #     # Meng-assign nomor setoran ke dalam order pengiriman meskipun statusnya masih draft
        #     # Untuk membantu proses perubahan atau update biaya fee (jika ada)
        #     record.nomor_setoran = result.kode_order_setoran
        #
        #     detail_order_dict = {
        #         'order_pengiriman': record.id,
        #         'create_date': record.create_date,
        #         'jenis_order': record.jenis_order,
        #         'customer_id': record.customer.id,
        #         'plant': record.plant.id if record.plant else None,
        #         'total_ongkos': record.total_ongkos_do or record.total_ongkos_reguler
        #     }
        #     detail_order.append(detail_order_dict)
        #
        # ############################## Membuat Dictionary-List Uang Jalan ###########################
        #
        #     for uang_jalan in record.uang_jalan:
        #         if uang_jalan.id not in record_uang_jalan:
        #             list_uang_jalan_dict = {
        #                 'tanggal': uang_jalan.create_date,
        #                 'uang_jalan_name': uang_jalan.id,
        #                 'total': uang_jalan.total,
        #                 'keterangan': uang_jalan.keterangan,
        #             }
        #             list_uang_jalan.append(list_uang_jalan_dict)
        #             record_uang_jalan.append(int(uang_jalan.id))
        #
        # ############################## Membuat Dictionary-List Pembelian ###########################
        #
        #     if record.biaya_pembelian:
        #         for item in record.biaya_pembelian:
        #             detail_list_pembelian_dict = {
        #                 'order_pengiriman': item.order_pengiriman.id,
        #                 'supplier': item.supplier.id,
        #                 'nama_barang': item.nama_barang,
        #                 'ukuran': item.ukuran,
        #                 'nominal': item.nominal,
        #             }
        #
        #             list_pembelian.append(detail_list_pembelian_dict)
        #
        # ############################## Membuat Dictionary-List Fee ################################
        #
        #     if record.biaya_fee:
        #         for item in record.biaya_fee:
        #             detail_list_biaya_fee_dict = {
        #                 'order_pengiriman': item.order_pengiriman.id,
        #                 'fee_contact': item.fee_contact.id,
        #                 'nominal': item.nominal,
        #             }
        #
        #             list_biaya_fee.append(detail_list_biaya_fee_dict)
        #
        # ############################## Mengeksekusi Create Record ################################
        #
        # # Membuat detail order
        # for item in detail_order:
        #     self.env['detail.order'].create([{
        #         'company_id': self.env.company.id,
        #         'order_setoran': result.id,
        #         'order_pengiriman': item['order_pengiriman'],
        #         'tanggal_order': item['create_date'],
        #         'jenis_order': item['jenis_order'],
        #         'customer': item['customer_id'],
        #         'plant': item['plant'],
        #         'jumlah': item['total_ongkos'],
        #     }])
        #
        # # Membuat detail list uang jalan
        # for item in list_uang_jalan:
        #     self.env['detail.list.uang.jalan'].create([{
        #         'company_id': self.env.company.id,
        #         'order_setoran': result.id,
        #         'tanggal': item['tanggal'],
        #         'uang_jalan_name': item['uang_jalan_name'],
        #         'total': item['total'],
        #         'keterangan': item['keterangan'],
        #     }])
        #
        # # Membuat list pembelian
        # for item in list_pembelian:
        #     self.env['detail.list.pembelian'].create([{
        #         'company_id': self.env.company.id,
        #         'order_setoran': result.id,
        #         'order_pengiriman': item['order_pengiriman'],
        #         'supplier': item['supplier'],
        #         'nama_barang': item['nama_barang'],
        #         'ukuran': item['ukuran'],
        #         'nominal': item['nominal'],
        #     }])
        #
        # # Membuat list biaya fee
        # for item in list_biaya_fee:
        #     self.env['detail.biaya.fee'].create([{
        #         'company_id': self.env.company.id,
        #         'order_setoran': result.id,
        #         'order_pengiriman': item['order_pengiriman'],
        #         'fee_contact': item['fee_contact'],
        #         'nominal': item['nominal'],
        #     }])
        #
        # order_pengiriman_model = self.env['order.pengiriman'].search([
        #     ('kendaraan', '=', vals.get('kendaraan', self.kendaraan.id)),
        #     ('sopir', '=', vals.get('sopir', self.sopir.id)),
        #     ('kenek', '=', vals.get('kenek', self.kenek.id)),
        #     ('state', '=', 'selesai'),
        #     ('company_id', '=', int(self.env.company.id))
        # ])
        #
        # if not order_pengiriman_model:
        #     self.env.user.notify_warning(message='Order pengiriman dengan kriteria kendaraan, sopir, dan kenek yang Anda pilih tidak ditemukan. Pastikan Order Pengiriman ada dan berstatus "Selesai".', sticky=True, title='Setoran ' + str(vals.get('kode_order_setoran')) + ' : Detail Order Tidak Ditemukan')
        # else:
        #     pass

        return result
    #
    # def write(self, vals):
    #     res = super(OrderSetoran, self).write(vals)

        # if 'detail_order' in vals:
        #     for uang_jalan in self.list_uang_jalan:
        #         uang_jalan.unlink()
        #
        #     for pembelian in self.list_pembelian:
        #         pembelian.unlink()
        #
        #     for biaya_fee in self.biaya_fee:
        #         biaya_fee.unlink()
        #
        #     list_uang_jalan = []
        #     for order in self.detail_order:
        #         # Buat Pembelian
        #         for pembelian in order.order_pengiriman.biaya_pembelian:
        #             self.list_pembelian.create({
        #                 'order_pengiriman': order.order_pengiriman.id,
        #                 'order_setoran': self.id,
        #                 'supplier': pembelian.supplier.id,
        #                 'nama_barang': pembelian.nama_barang,
        #                 'ukuran': pembelian.ukuran,
        #                 'nominal': pembelian.nominal,
        #             })
        #
        #         # Buat Biaya Fee
        #         for biaya_fee in order.order_pengiriman.biaya_fee:
        #             self.biaya_fee.create({
        #                 'order_pengiriman': order.order_pengiriman.id,
        #                 'order_setoran': self.id,
        #                 'fee_contact': biaya_fee.fee_contact.id,
        #                 'nominal': biaya_fee.nominal,
        #             })
        #
        #         # Appending Uang Jalan
        #         for uang_jalan in order.order_pengiriman.uang_jalan:
        #             list_uang_jalan.append({
        #                 'tanggal_uang_jalan': uang_jalan.create_date,
        #                 'uang_jalan_id': uang_jalan.id,
        #                 'total': uang_jalan.total,
        #                 'keterangan': uang_jalan.keterangan,
        #                 'order_id': order.order_pengiriman.id,
        #             })
        #
        #     # Remove duplicate uang jalan
        #     unique_list = []
        #     seen_ids = set()
        #     for item in list_uang_jalan:
        #         uang_jalan_id = item['uang_jalan_id']
        #         if uang_jalan_id not in seen_ids:
        #             unique_list.append(item)
        #             seen_ids.add(uang_jalan_id)
        #
        #     # Buat Uang Jalan
        #     for item in unique_list:
        #         self.list_uang_jalan.create({
        #             'company_id': self.env.company.id,
        #             'order_pengiriman': item['order_id'],
        #             'order_setoran': self.id,
        #             'tanggal': item['tanggal_uang_jalan'],
        #             'uang_jalan_name': item['uang_jalan_id'],
        #             'total': item['total'],
        #             'keterangan': item['keterangan'],
        #         })
        #

        # if 'kendaraan' in vals or 'sopir' in vals or 'kenek' in vals:
        #
        #     ############################## Rewrite Dictionary-List Detail Order ###########################
        #
        #     for record in self.detail_order:
        #         record.order_pengiriman.nomor_surat_jalan = None
        #         record.unlink()
        #
        #     for record in self.list_uang_jalan:
        #         record.unlink()
        #
        #     for record in self.list_pembelian:
        #         record.unlink()
        #
        #     for record in self.biaya_fee:
        #         record.unlink()
        #
        #     # list utama untuk membuat record pada tiap notebook
        #     detail_order = []
        #     list_uang_jalan = []
        #     list_pembelian = []
        #     list_biaya_fee = []
        #
        #     # List ini untuk menghindari double input pada setoran
        #     record_uang_jalan = []
        #
        #     order_pengiriman_model = self.env['order.pengiriman'].search([
        #         ('kendaraan', '=', vals.get('kendaraan', self.kendaraan.id)),
        #         ('sopir', '=', vals.get('sopir', self.sopir.id)),
        #         ('kenek', '=', vals.get('kenek', self.kenek.id)),
        #         ('state', '=', 'selesai'),
        #         ('company_id', '=', int(self.env.company.id))
        #     ])
        #
        #     if not order_pengiriman_model:
        #         self.env.user.notify_warning(
        #             message='Order pengiriman dengan kriteria kendaraan, sopir, dan kenek yang Anda pilih tidak ditemukan. Pastikan Order Pengiriman ada dan berstatus "Selesai".', sticky=True, title='Setoran ' + str(self.kode_order_setoran) + ' : Detail Order Tidak Ditemukan')
        #     else:
        #         pass
        #
        #     for record in order_pengiriman_model:
        #         detail_order_dict = {
        #             'order_pengiriman': record.id,
        #             'create_date': record.create_date,
        #             'jenis_order': record.jenis_order,
        #             'customer_id': record.customer.id,
        #             'plant': record.plant.id if record.plant else None,
        #             'total_ongkos': record.total_ongkos_do or record.total_ongkos_reguler
        #         }
        #         detail_order.append(detail_order_dict)
        #
        #     ############################## Rewrite Dictionary-List List Uang Jalan ###########################
        #
        #         for uang_jalan in record.uang_jalan:
        #             if uang_jalan.id not in record_uang_jalan:
        #                 list_uang_jalan_dict = {
        #                     'tanggal': uang_jalan.create_date,
        #                     'uang_jalan_name': uang_jalan.id,
        #                     'total': uang_jalan.total,
        #                     'keterangan': uang_jalan.keterangan,
        #                 }
        #                 list_uang_jalan.append(list_uang_jalan_dict)
        #                 record_uang_jalan.append(int(uang_jalan.id))
        #
        #     ############################## Rewrite Dictionary-List List Pembelian ###########################
        #
        #         if record.biaya_pembelian:
        #             for item in record.biaya_pembelian:
        #                 detail_list_pembelian_dict = {
        #                     'order_pengiriman': record.id,
        #                     'supplier': item.supplier.id,
        #                     'nama_barang': item.nama_barang,
        #                     'ukuran': item.ukuran,
        #                     'nominal': item.nominal,
        #                 }
        #
        #                 list_pembelian.append(detail_list_pembelian_dict)
        #
        #     ############################## Rewrite Dictionary-List Biaya Fee ###########################
        #
        #         # membuat list pembelian
        #         if record.biaya_fee:
        #             for item in record.biaya_fee:
        #                 detail_list_biaya_fee_dict = {
        #                     'order_pengiriman': record.id,
        #                     'fee_contact': item.fee_contact.id,
        #                     'nominal': item.nominal,
        #                 }
        #                 list_biaya_fee.append(detail_list_biaya_fee_dict)
        #
        #     ############################## Mengeksekusi WriteRecord ################################
        #
        #     for record in detail_order:
        #         self.env['detail.order'].create([{
        #             'company_id': self.env.company.id,
        #             'order_setoran': self.id,
        #             'order_pengiriman': record['order_pengiriman'],
        #             'tanggal_order': record['create_date'],
        #             'jenis_order': record['jenis_order'],
        #             'customer': record['customer_id'],
        #             'plant': record['plant'],
        #             'jumlah': record['total_ongkos'],
        #         }])
        #
        #     for record in list_uang_jalan:
        #         self.env['detail.list.uang.jalan'].create([{
        #             'company_id': self.env.company.id,
        #             'order_setoran': self.id,
        #             'tanggal': record['tanggal'],
        #             'uang_jalan_name': record['uang_jalan_name'],
        #             'total': record['total'],
        #             'keterangan': record['keterangan'],
        #     }])
        #
        #     for record in list_pembelian:
        #         self.env['detail.list.pembelian'].create([{
        #             'company_id': self.env.company.id,
        #             'order_setoran': self.id,
        #             'order_pengiriman': record['order_pengiriman'],
        #             'supplier': record['supplier'],
        #             'nama_barang': record['nama_barang'],
        #             'ukuran': record['ukuran'],
        #             'nominal': record['nominal'],
        #         }])
        #
        #     for record in list_biaya_fee:
        #         self.env['detail.biaya.fee'].create([{
        #             'company_id': self.env.company.id,
        #             'order_setoran': self.id,
        #             'order_pengiriman': record['order_pengiriman'],
        #             'fee_contact': record['fee_contact'],
        #             'nominal': record['nominal'],
        #         }])

        # res = super(OrderSetoran, self).write(vals)

        # # Cek apakah ada penambahan atau perubahan biaya_fee
        # if 'biaya_fee' in vals:
        #     biaya_fee_list_before_updated = []
        #     # Rewriting Biaya Fee di dalam order setoran
        #     for record in self.biaya_fee:
        #         biaya_fee_before_update_dict = {
        #             'order_setoran': self.id,
        #             'order_pengiriman': record.order_pengiriman.id,
        #             'fee_contact': record.fee_contact.id,
        #             'nominal': record.nominal,
        #         }
        #
        #         biaya_fee_list_before_updated.append(biaya_fee_before_update_dict)
        #
        #         record.unlink()
        #
        #     for item in biaya_fee_list_before_updated:
        #         self.env['detail.biaya.fee'].create({
        #             'company_id': self.env.company.id,
        #             'order_setoran': self.id,
        #             'order_pengiriman': item['order_pengiriman'],
        #             'fee_contact': item['fee_contact'],
        #             'nominal': item['nominal'],
        #         })
        #
        #     # Rewriting Biaya Fee di order pengiriman
        #     biaya_fee_order_pengiriman = []
        #     for item in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_fee:
        #         fee_dict = {
        #             'order_pengiriman': item.order_pengiriman.id,
        #             'fee_contact': item.fee_contact.id,
        #             'nominal': item.nominal,
        #         }
        #
        #         biaya_fee_order_pengiriman.append(fee_dict)
        #
        #     for record in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_fee:
        #         record.unlink()
        #
        #     for item in biaya_fee_list_before_updated:
        #         self.env['biaya.fee'].create({
        #             'company_id': self.env.company.id,
        #             'order_pengiriman': item['order_pengiriman'],
        #             'fee_contact': item['fee_contact'],
        #             'nominal': item['nominal'],
        #         })
        #
        # # Cek apakah ada penambahan atau perubahan List Pembelian
        # if 'list_pembelian' in vals:
        #     list_pembelian_before_updated = []
        #     # Rewriting List Pembelian di dalam order setoran
        #     for record in self.list_pembelian:
        #         list_pembelian_before_update_dict = {
        #             'order_setoran': self.id,
        #             'order_pengiriman': record.order_pengiriman.id,
        #             'supplier': record.supplier.id,
        #             'nama_barang': record.nama_barang,
        #             'nominal': record.nominal,
        #         }
        #
        #         list_pembelian_before_updated.append(list_pembelian_before_update_dict)
        #
        #         record.unlink()
        #
        #     for item in list_pembelian_before_updated:
        #         self.env['detail.list.pembelian'].create({
        #             'company_id': self.env.company.id,
        #             'order_setoran': self.id,
        #             'order_pengiriman': item['order_pengiriman'],
        #             'supplier': item['supplier'],
        #             'nama_barang': item['nama_barang'],
        #             'nominal': item['nominal'],
        #         })
        #
        #     # Rewriting Biaya Fee di order pengiriman
        #     list_pembelian_order_pengiriman = []
        #     for item in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_pembelian:
        #         list_pembelian_dict = {
        #             'order_pengiriman': item.order_pengiriman.id,
        #             'supplier': item.supplier.id,
        #             'nama_barang': item.nama_barang,
        #             'nominal': item.nominal,
        #         }
        #
        #         list_pembelian_order_pengiriman.append(list_pembelian_dict)
        #
        #     for record in self.env['order.pengiriman'].search([('nomor_setoran', '=', self.kode_order_setoran)]).biaya_pembelian:
        #         record.unlink()
        #
        #     for item in list_pembelian_before_updated:
        #         self.env['biaya.pembelian'].create({
        #             'company_id': self.env.company.id,
        #             'order_pengiriman': item['order_pengiriman'],
        #             'supplier': item['supplier'],
        #             'nama_barang': item['nama_barang'],
        #             'nominal': item['nominal'],
        #         })

        # return res


    def write(self, vals):
        if 'detail_order' in vals:
            if 'detail_order' in vals:
                # Retrieve existing detail_order records and their order_pengiriman before the update
                existing_detail_orders = self.mapped('detail_order')
                existing_detail_orders_dict = {rec.id: rec.order_pengiriman.id for rec in existing_detail_orders}

                # Call the super method to perform the write
                result = super(OrderSetoran, self).write(vals)

                # Retrieve updated detail_order records and their order_pengiriman after the update
                updated_detail_orders = self.mapped('detail_order')
                updated_detail_orders_dict = {rec.id: rec.order_pengiriman.id for rec in updated_detail_orders}

                # Determine deleted detail_order records by comparing the sets
                deleted_detail_orders = set(existing_detail_orders_dict.keys()) - set(updated_detail_orders_dict.keys())
                deleted_order_pengiriman_ids = [existing_detail_orders_dict[rec_id] for rec_id in deleted_detail_orders]
                # print("Deleted order_pengiriman IDs:", deleted_order_pengiriman_ids)

                # Now you can handle the deleted records as needed
                # For example, logging or performing additional actions
                for line in self.list_pembelian:
                    if line.order_pengiriman.id in deleted_order_pengiriman_ids:
                        line.unlink()

                for line in self.biaya_fee:
                    if line.order_pengiriman.id in deleted_order_pengiriman_ids:
                        line.unlink()

                for order_pengiriman_id in deleted_order_pengiriman_ids:
                    self.env['order.pengiriman'].search([('id', '=', order_pengiriman_id)]).unlink()

                return result
            else:
                return super(OrderSetoran, self).write(vals)

        return super(OrderSetoran, self).write(vals)

    def create_regular_op(self):
        context = {
            'created_from_setoran': True,
            'order_setoran_id': self.id,
            'default_jenis_order': 'regular',
            'default_kendaraan_id': self.kendaraan.id,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('order_pengiriman.order_pengiriman_form_view').id,
            'res_model': 'order.pengiriman',
            'target': 'new',
            'context': context,
        }

    def create_do_op(self):
        context = {
            'created_from_setoran': True,
            'order_setoran_id': self.id,
            'default_jenis_order': 'do',
            'default_kendaraan_id': self.kendaraan.id,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('order_pengiriman.order_pengiriman_form_view').id,
            'res_model': 'order.pengiriman',
            'target': 'new',
            'context': context,
        }

class DetailOrder(models.Model):
    _name = 'detail.order'
    _description = 'Detail Order'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_setoran = fields.Many2one('order.setoran', invisible=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
    tanggal_order = fields.Datetime('Tanggal')
    customer = fields.Many2one('res.partner', 'Customer', tracking=True, related="order_pengiriman.customer")
    plant = fields.Many2one('konfigurasi.plant', 'PLANT', tracking=True, related="order_pengiriman.plant")
    nomor_surat_jalan = fields.Char('Nomor')
    jumlah = fields.Float('Jumlah', digits=(6, 0), related="order_pengiriman.total_ongkos")
    bayar_dimuka = fields.Float('Bayar Dimuka', digits=(6, 0))
    jenis_order = fields.Selection([
        ('do', 'DO'),
        ('regular', 'Regular'),
    ], required=True, string="Jenis", tracking=True, related="order_pengiriman.jenis_order")

    @api.constrains('bayar_dimuka', 'jumlah')
    def _check_bayar_dimuka(self):
        for record in self:
            if record.bayar_dimuka > record.jumlah:
                raise ValidationError('Nominal bayar dimuka lebih besar daripada nominal yang ditagihkan (' +(record.order_pengiriman.order_pengiriman_name) + ').' )

    @api.onchange('order_pengiriman')
    def onchange_order_pengiriman(self):
        for order in self.order_pengiriman:
            self.company_id = self.env.company.id
            self.tanggal_order = order.create_date
            self.jenis_order = order.jenis_order
            self.customer = order.customer.id
            self.plant = order.plant
            self.jumlah = order.total_ongkos

class ListUangJalan(models.Model):
    _name = 'detail.list.uang.jalan'
    _description = 'List Uang Jalan'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    # order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
    order_setoran = fields.Many2one('order.setoran', invisible=True)
    tanggal = fields.Date('Tanggal')
    uang_jalan_name = fields.Many2one('uang.jalan', 'No Uang Jalan')
    total = fields.Float('Total', digits=(6, 0), related="uang_jalan_name.total")
    keterangan = fields.Text('Keterangan', related="uang_jalan_name.keterangan")

# class ListPembelian(models.Model):
#     _name = 'detail.list.pembelian'
#     _description = 'List Pembelian'
#
#     company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
#     order_setoran = fields.Many2one('order.setoran', invisible=True)
#     order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
#     supplier = fields.Many2one('res.partner', 'Supplier')
#     nama_barang = fields.Char('Nama')
#     ukuran = fields.Text('Ukuran')
#     nominal = fields.Float('Biaya', digits=(6, 0))

# class BiayaFee(models.Model):
#     _name = 'detail.biaya.fee'
#     _description = 'Biaya Fee'
#
#     company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
#     order_setoran = fields.Many2one('order.setoran', invisible=True)
#     order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
#     fee_contact = fields.Many2one('res.partner', 'Nama')
#     nominal = fields.Float('Nominal', digits=(6, 0))

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