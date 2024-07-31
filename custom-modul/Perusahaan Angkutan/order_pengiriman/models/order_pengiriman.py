import datetime

from odoo import api, models, fields
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import itertools

class OrderPengiriman(models.Model):
    _name = 'order.pengiriman'
    _description = 'Order Pengiriman'
    _inherit = ['mail.thread']
    _rec_name = 'order_pengiriman_name'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    state = fields.Selection([
        ('order_baru', "Order Baru"),
        ('dalam_perjalanan', "Dalam Perjalanan"),
        ('selesai', "Selesai"),
        ('sudah_setor', "Sudah Setor"),
        ('batal', "Batal"),
    ], default='order_baru', string="State", group_expand='_expand_states', index=True, hide=True, tracking=True)

    active = fields.Boolean('Archive', default=True, tracking=True)


    is_sudah_disetor = fields.Boolean()
    is_uang_jalan_terbit = fields.Boolean()
    is_oper_order = fields.Boolean(store=True)
    order_pengiriman_name = fields.Char(readonly=True, required=True, copy=False, default='New')
    customer = fields.Many2one('res.partner', 'Customer', required=True, ondelete='restrict', tracking=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    alamat_muat = fields.Many2one('konfigurasi.lokasi', required=True, ondelete='restrict', tracking=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', False)],
        'sudah_setor': [('readonly', False)],
    })

    detail_alamat_muat = fields.Text('Detail Alamat Muat', placeholder='Contoh : Jalan Mangga RT 50 No 2', tracking=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', False)],
        'sudah_setor': [('readonly', False)],
    })

    tanggal_estimasi_muat = fields.Date(string='Estimasi Tanggal Muat', tracking=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    alamat_bongkar = fields.Many2one('konfigurasi.lokasi', required=True, ondelete='restrict', tracking=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', False)],
        'sudah_setor': [('readonly', False)],
    })

    detail_alamat_bongkar = fields.Text('Detail Alamat Bongkar', placeholder='Contoh : Jalan Bersama Blok C No 23', tracking=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', False)],
        'sudah_setor': [('readonly', False)],
    })

    tanggal_order = fields.Date(string='Tanggal Order', tracking=True, digits=(6, 0), default=fields.Date.today(), states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    tanggal_estimasi_bongkar = fields.Date(string='Estimasi Tanggal Bongkar', tracking=True, digits=(6, 0), states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    total_biaya_fee = fields.Float(compute='_compute_total_biaya_fee', store=True, tracking=True, digits=(6, 0), states={
        'order_baru': [('readonly', True)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    total_biaya_pembelian = fields.Float(compute='_compute_total_biaya_pembelian', store=True, tracking=True, digits=(6, 0), states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    total_ongkos_do = fields.Float(compute='_compute_total_ongkos_do', store=True, tracking=True, digits=(6, 0), states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    total_ongkos_reguler = fields.Float(compute='_compute_total_ongkos_reguler', store=True, tracking=True, digits=(6, 0), states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    total_ongkos = fields.Float(compute='_compute_total_ongkos', store=True, digits=(6, 0))

    total_uang_jalan = fields.Float('Uang Jalan', compute='_compute_total_uang_jalan', copy=False, digits=(6, 0), states={
        'order_baru': [('readonly', True)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    jenis_order = fields.Selection([
        ('do', 'DO'),
        ('regular', 'Regular'),
    ], required=True, default='do', tracking=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    detail_order_do = fields.One2many('detail.order.do', 'order_pengiriman', copy=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    detail_order_reguler = fields.One2many('detail.order.reguler', 'order_pengiriman', copy=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    biaya_pembelian = fields.One2many('biaya.pembelian', 'order_pengiriman', copy=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', False)],
        'sudah_setor': [('readonly', False)],
    })

    biaya_fee = fields.One2many('biaya.fee', 'order_pengiriman', copy=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', False)],
        'sudah_setor': [('readonly', False)],
    })

    plant = fields.Many2one('konfigurasi.plant', 'PLANT', ondelete='restrict', tracking=True, copy=True, states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', True)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
    })

    uang_jalan = fields.Many2many('uang.jalan', string='No. Uang Jalan', store=True, copy=False, domain=[('state', 'in', ['paid', 'closed'])], states={
        'order_baru': [('readonly', False)],
        'dalam_perjalanan': [('readonly', False)],
        'selesai': [('readonly', True)],
        'sudah_setor': [('readonly', True)],
        'batal': [('readonly', True)],
    })

    nomor_setoran = fields.Char('Nomor Setoran')
    oper_setoran = fields.Char('Oper Setoran')

    oper_order = fields.Many2one('oper.order', 'No. Oper Order', readonly=True, store=True, copy=False)
    sopir = fields.Many2one('hr.employee', 'Sopir', readonly=True, store=True, copy=False)
    kenek = fields.Many2one('hr.employee', 'Kenek', readonly=True, store=True, copy=False)
    kendaraan = fields.Many2one('fleet.vehicle', 'Kendaraan', readonly=True, store=True, copy=False)
    model_kendaraan = fields.Char(string='Model Kendaraan', readonly=True, store=True, copy=False)
    nomor_kendaraan = fields.Char(string='Nomor Kendaraan',readonly=True, store=True, copy=False)
    nomor_surat_jalan = fields.Char('No Surat Jalan', copy=False)
    vendor_pa = fields.Many2one('res.partner', 'Vendor PA', readonly=True, store=True, copy=False)


    def buat_uang_jalan(self, records):
        uang_jalan_records = []

        uang_jalan = self.env['uang.jalan'].create({
            'kendaraan': None,
            'sopir': None,
            'kenek': None,
            'create_date': fields.Datetime.now(),
        })

        uang_jalan_line_values = []
        for item in records:

            konfigurasi_tipe_muatan_id = self.env['konfigurasi.tipe.muatan'].search([], limit=1).id
            uang_jalan_line_values.append({
                'uang_jalan':uang_jalan.id,
                'order_pengiriman': item.id,
                'tipe_muatan': konfigurasi_tipe_muatan_id,
                'muat': item.alamat_muat.id,
                'bongkar': item.alamat_bongkar.id,
            })

        uang_jalan_lines = self.env['uang.jalan.line'].create(uang_jalan_line_values)

        self.env.user.notify_success(message='Pembuatan Uang Jalan Berhasil', title='Sukses')

        return {
            'name': 'Uang Jalan Form',
            'type': 'ir.actions.act_window',
            'res_model': 'uang.jalan',
            'view_mode': 'form',
            'res_id': uang_jalan.id,
            'view_id': self.env.ref('order_pengiriman.uang_jalan_form_view').id,  # Replace with the actual form view ID
            'target': 'main',
        }

    def buat_oper_order(self, records):
        oper_order_records = []

        oper_order = self.env['oper.order'].create({
            'vendor_pa': None,
            'kendaraan': None,
            'create_date': fields.Datetime.now(),
        })

        oper_order_line_values = []
        for item in records:
            oper_order_line_values.append({
                'oper_order':oper_order.id,
                'order_pengiriman': item.id,
                'muat': item.alamat_muat.id,
                'bongkar': item.alamat_bongkar.id,
            })

        oper_order_lines = self.env['oper.order.line'].create(oper_order_line_values)

        self.env.user.notify_success(message='Pembuatan Oper Order Berhasil', title='Sukses')

        return {
            'name': 'Oper Order Form',
            'type': 'ir.actions.act_window',
            'res_model': 'oper.order',
            'view_mode': 'form',
            'res_id': oper_order.id,
            'view_id': self.env.ref('order_pengiriman.oper_order_form_view').id,  # Replace with the actual form view ID
            'target': 'main',
        }

    def write(self, vals):
        if 'state' in vals:
            current_state = self.state
            selected_state = vals['state'] or None

            if 'is_uang_jalan_terbit' in vals:
                pass
            elif 'is_sudah_disetor' in vals:
                pass
            else:
                # Order Baru
                if current_state == 'order_baru' and selected_state == 'dalam_perjalanan' and 'uang_jalan' in vals:
                    raise ValidationError('Anda harus membuat Uang Jalan untuk mengubah status Order Pengiriman ini.')
                elif current_state == 'dalam_perjalanan' and selected_state == 'order_baru' and 'uang_jalan' in vals:
                    raise ValidationError('Uang jalan telah terbuat untuk Order Pengiriman ini. Silahkan batalkan uang jalan yang sudah dibuat.')
                elif current_state == 'order_baru' and selected_state == 'selesai':
                    raise ValidationError('Anda tidak dapat mengubah status order baru menjadi selesai dalam sekali proses.')
                elif current_state == 'selesai' and selected_state == 'order_baru':
                    raise ValidationError('Anda tidak dapat mengubah status dari selesai menjadi order baru dalam sekali proses.')

                # Selesai
                elif current_state == 'selesai' and selected_state == 'sudah_setor':
                    raise ValidationError('Anda tidak dapat mengubah status melalui metode ini. Anda harus membuat setoran untuk melakukannya.')
                elif current_state == 'sudah_setor' and selected_state == 'selesai':
                    raise ValidationError('Anda tidak dapat mengubah status melalui metode ini karena setoran telah berhasil dibuat untuk order pengiriman ini.')

        if 'uang_jalan' in vals:
            if vals['uang_jalan'] == None:
                pass
            elif bool(vals['uang_jalan'][0][2]) == True:
                self.sudo().write({'state': 'dalam_perjalanan'})

                try:
                    for item in vals['uang_jalan'][0][2]:
                        uang_jalan = self.env['uang.jalan'].search([('id', '=', item)])
                except:
                    if vals['uang_jalan'][0][2]:
                        uang_jalan = self.env['uang.jalan'].search([('id', '=', int(vals['uang_jalan'][0][2]))])

                if bool(vals['uang_jalan'][0][2]):
                    vals['state'] = 'dalam_perjalanan'
                    if len(vals['uang_jalan'][0][2]) > 1:
                        raise UserError(
                            'Uang jalan "Nominal Saja" harus menggunakan satu surat jalan saja pada Order Pengiriman ini.')
                    else:
                        uang_jalan = self.env['uang.jalan'].search([('id', '=', vals['uang_jalan'][0][2][0])])
                        vals['sopir'] = uang_jalan.sopir.id
                        vals['kenek'] = uang_jalan.kenek.id
                        vals['nomor_kendaraan'] = uang_jalan.kendaraan.license_plate
                        vals['model_kendaraan'] = uang_jalan.kendaraan.model_id.name
                        vals['kendaraan'] = uang_jalan.kendaraan.id

            elif bool(vals['uang_jalan'][0][2]) == False:
                self.sudo().write({'state': 'order_baru'})

                try:
                    for item in vals['uang_jalan'][0][2]:
                        uang_jalan = self.env['uang.jalan'].search([('id', '=', item)])
                except:
                    if vals['uang_jalan'][0][2]:
                        uang_jalan = self.env['uang.jalan'].search([('id', '=', int(vals['uang_jalan'][0][2]))])

                # Mengassign Order pengiriman dengan data uang jalan
                if vals['uang_jalan'][0][2] != 0:
                    vals['sopir'] = None
                    vals['kenek'] = None
                    vals['nomor_kendaraan'] = None
                    vals['model_kendaraan'] = None
                    vals['kendaraan'] = None

        res = super(OrderPengiriman, self).write(vals)

        # Cek apakah ada penambahan atau perubahan biaya_fee
        if 'biaya_fee' in vals:
            if self.nomor_setoran:
                # Rewriting Biaya Fee di dalam order pengiriman
                biaya_fee_list = []
                for record in self.biaya_fee:
                    fee_dict = {
                        'order_pengiriman': self.id,
                        'fee_contact': record.fee_contact.id,
                        'nominal': record.nominal,
                    }

                    biaya_fee_list.append(fee_dict)

                    record.unlink()

                for item in biaya_fee_list:
                    self.env['biaya.fee'].create({
                        'company_id': self.env.company.id,
                        'order_pengiriman': item['order_pengiriman'],
                        'fee_contact': item['fee_contact'],
                        'nominal': item['nominal'],
                    })

                # Rewriting Biaya Fee di order setoran
                biaya_fee_setoran_list = []
                for item in self.env['order.setoran'].search([('kode_order_setoran', '=', self.nomor_setoran)]).biaya_fee:
                    fee_dict = {
                        'order_pengiriman': item.order_pengiriman.id,
                        'fee_contact': item.fee_contact.id,
                        'nominal': item.nominal,
                    }

                    biaya_fee_setoran_list.append(fee_dict)

                for record in self.env['order.setoran'].search([('kode_order_setoran', '=', self.nomor_setoran)]).biaya_fee:
                    if str(record.order_pengiriman.order_pengiriman_name) == str(self.order_pengiriman_name):
                        record.unlink()

                for item in biaya_fee_list:
                    self.env['detail.biaya.fee'].create({
                        'company_id': self.env.company.id,
                        'order_setoran': self.env['order.setoran'].search([('kode_order_setoran', '=', self.nomor_setoran)]).id,
                        'order_pengiriman': item['order_pengiriman'],
                        'fee_contact': item['fee_contact'],
                        'nominal': item['nominal'],
                    })

            elif self.oper_setoran:
                # Rewriting Biaya Fee di dalam order pengiriman
                biaya_fee_list = []
                for record in self.biaya_fee:
                    fee_dict = {
                        'order_pengiriman': self.id,
                        'fee_contact': record.fee_contact.id,
                        'nominal': record.nominal,
                    }

                    biaya_fee_list.append(fee_dict)

                    record.unlink()

                for item in biaya_fee_list:
                    self.env['biaya.fee'].create({
                        'company_id': self.env.company.id,
                        'order_pengiriman': item['order_pengiriman'],
                        'fee_contact': item['fee_contact'],
                        'nominal': item['nominal'],
                    })

                # Rewriting Biaya Fee di oper setoran
                biaya_fee_setoran_list = []
                for item in self.env['oper.setoran'].search([('kode_oper_setoran', '=', self.oper_setoran)]).biaya_fee_setoran:
                    fee_dict = {
                        'order_pengiriman': item.order_pengiriman.id,
                        'nominal': item.nominal,
                    }

                    biaya_fee_setoran_list.append(fee_dict)

                for record in self.env['oper.setoran'].search([('kode_oper_setoran', '=', self.oper_setoran)]).biaya_fee_setoran:
                    if record.order_pengiriman.id == self.id:
                        record.unlink()

                self.env['biaya.fee.setoran'].create({
                    'company_id': self.env.company.id,
                    'oper_setoran': self.env['oper.setoran'].search([('kode_oper_setoran', '=', self.oper_setoran)]).id,
                    'order_pengiriman': self.id,
                    'nominal': self.total_biaya_fee,
                })

        # Cek apakah ada penambahan atau perubahan biaya_pembelian
        if 'biaya_pembelian' in vals:
            if self.nomor_setoran:
                # Rewriting List Pembelian di dalam order pengiriman
                biaya_pembelian_list = []
                for record in self.biaya_pembelian:
                    biaya_pembelian_dict = {
                        'order_pengiriman': self.id,
                        'supplier': record.supplier.id,
                        'nama_barang': record.nama_barang,
                        'nominal': record.nominal,
                    }

                    biaya_pembelian_list.append(biaya_pembelian_dict)
                    record.unlink()

                for item in biaya_pembelian_list:
                    self.env['biaya.pembelian'].create({
                        'company_id': self.env.company.id,
                        'order_pengiriman': item['order_pengiriman'],
                        'supplier': item['supplier'],
                        'nama_barang': item['nama_barang'],
                        'nominal': item['nominal'],
                    })

                # Rewriting List Pembelian di order setoran
                biaya_pembelian_setoran_list = []
                for item in self.env['order.setoran'].search([('kode_order_setoran', '=', self.nomor_setoran)]).list_pembelian:
                    list_pembelian_dict = {
                        'order_pengiriman': item.order_pengiriman.id,
                        'supplier': item.supplier.id,
                        'nama_barang': item.nama_barang,
                        'nominal': item.nominal,
                    }
                    biaya_pembelian_setoran_list.append(list_pembelian_dict)
                for record in self.env['order.setoran'].search([('kode_order_setoran', '=', self.nomor_setoran)]).list_pembelian:
                    if str(record.order_pengiriman.order_pengiriman_name) == str(self.order_pengiriman_name):
                        record.unlink()

                for item in biaya_pembelian_list:
                    self.env['detail.list.pembelian'].create({
                        'company_id': self.env.company.id,
                        'order_setoran': self.env['order.setoran'].search([('kode_order_setoran', '=', self.nomor_setoran)]).id,
                        'order_pengiriman': item['order_pengiriman'],
                        'supplier': item['supplier'],
                        'nama_barang': item['nama_barang'],
                        'nominal': item['nominal'],
                    })

            elif self.oper_setoran:
                # Rewriting Biaya Pembelian di dalam order pengiriman
                biaya_pembelian_list = []
                for record in self.biaya_pembelian:
                    biaya_pembelian_dict = {
                        'order_pengiriman': self.id,
                        'supplier': record.supplier.id,
                        'nama_barang': record.nama_barang,
                        'nominal': record.nominal,
                    }

                    biaya_pembelian_list.append(biaya_pembelian_dict)

                    record.unlink()

                for item in biaya_pembelian_list:
                    self.env['biaya.pembelian'].create({
                        'company_id': self.env.company.id,
                        'order_pengiriman': item['order_pengiriman'],
                        'supplier': item['supplier'],
                        'nama_barang': item['nama_barang'],
                        'nominal': item['nominal'],
                    })

                # Rewriting Biaya Pembelian di oper setoran
                biaya_pembelian_setoran_list = []
                for item in self.env['oper.setoran'].search([('kode_oper_setoran', '=', self.oper_setoran)]).list_pembelian_setoran:
                    biaya_pembelian_dict = {
                        'order_pengiriman': item.order_pengiriman.id,
                        'nominal': item.nominal,
                    }

                    biaya_pembelian_setoran_list.append(biaya_pembelian_dict)

                for record in self.env['oper.setoran'].search([('kode_oper_setoran', '=', self.oper_setoran)]).list_pembelian_setoran:
                    if record.order_pengiriman.id == self.id:
                        record.unlink()

                self.env['list.pembelian.setoran'].create({
                    'company_id': self.env.company.id,
                    'oper_setoran': self.env['oper.setoran'].search([('kode_oper_setoran', '=', self.oper_setoran)]).id,
                    'order_pengiriman': self.id,
                    'nominal': self.total_biaya_pembelian,
                })


        return res

    def unlink(self):
        if any(record.state not in ('order_baru', 'batal') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'Draft' atau 'Cancel'.")

        return super(OrderPengiriman, self).unlink()

    def konfirmasi_pengiriman(self):
        self.state = 'selesai'

    def cancel(self):
        for record in self:
            # Cancel Uang Jalan
            if self.uang_jalan:
                # Cancel Order Setoran
                order_setoran = self.env['detail.order'].search([('order_pengiriman','=',self.order_pengiriman_name)])
                for order in order_setoran:
                    order.order_setoran.cancel()

                    # Cancel Invoice
                    invoices = self.env['account.move'].search([('nomor_setoran', '=', order.order_setoran.kode_order_setoran), ('move_type', '=', 'out_invoice')])
                    if bool(invoices):
                        for invoice in invoices:
                            invoice.button_cancel()

                    # Cancel Vendor Bill
                    bills = self.env['account.move'].search([('nomor_setoran', '=', order.order_setoran.kode_order_setoran), ('move_type', '=', 'in_invoice')])
                    if bool(bills):
                        for bill in bills:
                            bill.button_draft()
                            bill.button_cancel()

                    # Cancel Expense
                    expenses = self.env['hr.expense'].search([('reference', '=', order.order_setoran.kode_order_setoran)])
                    if bool(bills):
                        for expense in expenses:
                            expense.unlink()

                # Cancel Uang Jalan
                for record in self.uang_jalan:
                    record.cancel()

            elif self.oper_order:
                oper_setoran = self.env['detail.order.setoran'].search([('order_pengiriman', '=', self.order_pengiriman_name)])
                for order in oper_setoran:
                    order.oper_setoran.cancel()

                    # Cancel Invoice
                    invoices = self.env['account.move'].search([('nomor_setoran', '=', order.oper_setoran.kode_oper_setoran), ('move_type', '=', 'out_invoice')])
                    if bool(invoices):
                        for invoice in invoices:
                            invoice.button_cancel()

                    # Cancel Vendor Bill
                    bills = self.env['account.move'].search([('nomor_setoran', '=', order.oper_setoran.kode_oper_setoran), ('move_type', '=', 'in_invoice')])
                    if bool(bills):
                        for bill in bills:
                            bill.button_draft()
                            bill.button_cancel()

                # Cancel Oper Order
                for record in self.oper_order:
                    record.cancel()

            self.state = 'batal'

    # Method untuk auto name assignment
    @api.model
    def create(self, vals):
        vals['order_pengiriman_name'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('order.pengiriman.sequence')

        try:
            if bool(vals['uang_jalan'][0][2]):
                vals['state'] = 'dalam_perjalanan'
                if len(vals['uang_jalan'][0][2]) > 1:
                    raise UserError('Uang jalan "Nominal Saja" harus menggunakan satu surat jalan saja pada Order Pengiriman ini.')
                else:
                    uang_jalan = self.env['uang.jalan'].search([('id', '=',vals['uang_jalan'][0][2][0])])
                    vals['sopir'] = uang_jalan.sopir.id
                    vals['kenek'] = uang_jalan.kenek.id
                    vals['nomor_kendaraan'] = uang_jalan.kendaraan.license_plate
                    vals['model_kendaraan'] = uang_jalan.kendaraan.model_id.name
                    vals['kendaraan'] = uang_jalan.kendaraan.id
        except:
            pass

        result = super(OrderPengiriman, self).create(vals)

        print(vals)

        context = self.env.context
        if 'created_from_setoran' in context:
            self.env['detail.order'].sudo().create({
                'order_setoran': context['order_setoran_id'],
                'order_pengiriman': result.id,
                'customer': vals['customer'],
                'tanggal_order': fields.Datetime.now(),
                'nomor_surat_jalan': vals['nomor_surat_jalan'] if 'nomor_surat_jalan' in vals else False,
                'plant': vals['plant'] if 'plant' in vals else False,
                'jumlah': float(vals['total_ongkos_reguler']) + float(vals['total_ongkos_do']),
            })

        return result

    # Method untuk menampilkan kanban
    def _expand_states(self, states, domain, order):
        return ['order_baru', 'dalam_perjalanan', 'selesai']

    # Method untuk menghitung total biaya fee
    @api.depends('biaya_fee.nominal')
    def _compute_total_biaya_fee(self):
        for record in self:
            record.total_biaya_fee = sum(record.biaya_fee.mapped('nominal'))

    @api.depends('biaya_pembelian.nominal')
    def _compute_total_biaya_pembelian(self):
        for record in self:
            record.total_biaya_pembelian = sum(record.biaya_pembelian.mapped('nominal'))

    # Method untuk menghitung subtotal ongkos jenis order DO
    @api.depends('detail_order_do.subtotal_ongkos')
    def _compute_total_ongkos_do(self):
        for record in self:
            record.total_ongkos_do = sum(record.detail_order_do.mapped('subtotal_ongkos'))

    # Method untuk menghitung subtotal ongkos jenis order reguler
    @api.depends('detail_order_reguler.subtotal_ongkos')
    def _compute_total_ongkos_reguler(self):
        for record in self:
            record.total_ongkos_reguler = sum(record.detail_order_reguler.mapped('subtotal_ongkos'))

    # Method untuk menghitung subtotal ongkos jenis order reguler
    @api.depends('total_ongkos_do', 'total_ongkos_reguler')
    def _compute_total_ongkos(self):
        for record in self:
            record.total_ongkos = record.total_ongkos_reguler or record.total_ongkos_do

    @api.onchange('jenis_order')
    def _reset_line(self):
        if self.jenis_order == 'do':
            self.plant = None
            for record in self.detail_order_do:
                record.unlink()
        if self.jenis_order == 'regular':
            for record in self.detail_order_reguler:
                record.unlink()

    @api.depends('uang_jalan')
    def _compute_total_uang_jalan(self):
        for rec in self:
            total = 0.0
            for uang_jalan in rec.uang_jalan:
                total += uang_jalan.total
            rec.total_uang_jalan = total


class DetailOrderDO(models.Model):
    _name = 'detail.order.do'
    _description = 'Detail Order DO'
    _rec_name = 'nama_barang'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_pengiriman = fields.Many2one('order.pengiriman', invisible=True)
    nama_barang = fields.Text('Nama Barang')
    keterangan_barang = fields.Text('Keterangan')
    ongkos_per_kg = fields.Float('Ongkos/Kg', digits=(6, 3))
    jumlah_per_kg = fields.Float('Jumlah(Kg)', digits=(6, 3))
    subtotal_ongkos = fields.Float('Subtotal Ongkos', compute='_compute_subtotal_ongkos_do', store=True, readonly=False, digits=(6, 0))

    @api.depends('ongkos_per_kg', 'jumlah_per_kg')
    def _compute_subtotal_ongkos_do(self):
        for record in self:
            record.subtotal_ongkos = record.ongkos_per_kg * record.jumlah_per_kg

class DetailOrderReguler(models.Model):
    _name = 'detail.order.reguler'
    _description = 'Detail Order Reguler'
    _rec_name = 'nama_barang'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_pengiriman = fields.Many2one('order.pengiriman', invisible=True)
    nama_barang = fields.Text('Nama Barang')
    keterangan_barang = fields.Text('Keterangan')
    panjang_barang = fields.Float('Panjang', digits=(6, 3))
    lebar_barang = fields.Float('Lebar', digits=(6, 3))
    tinggi_barang = fields.Float('Tinggi', digits=(6, 3))
    ongkos_volume = fields.Float('Ongkos/m3', digits=(6, 3))
    subtotal_ongkos = fields.Float('Subtotal Ongkos', compute='_compute_subtotal_ongkos_reguler', store=True, readonly=False, digits=(6, 0))

    @api.depends('panjang_barang', 'lebar_barang', 'tinggi_barang', 'ongkos_volume')
    def _compute_subtotal_ongkos_reguler(self):
        for record in self:
            record.subtotal_ongkos = (record.panjang_barang * record.lebar_barang * record.tinggi_barang) * record.ongkos_volume

class BiayaPembelian(models.Model):
    _name = 'biaya.pembelian'
    _description = 'Biaya Pembelian'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_pengiriman = fields.Many2one('order.pengiriman', invisible=True)
    supplier = fields.Many2one('res.partner', 'Supplier', ondelete='restrict')
    nama_barang = fields.Char('Nama Barang')
    ukuran = fields.Text('Ukuran')
    nominal = fields.Float('Nominal', digits=(6, 0))

class BiayaFee(models.Model):
    _name = 'biaya.fee'
    _description = 'Biaya Fee'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    order_pengiriman = fields.Many2one('order.pengiriman', invisible=True)
    fee_contact = fields.Many2one('res.partner', 'Name', ondelete='restrict')
    nominal = fields.Float('Nominal', digits=(6, 0))