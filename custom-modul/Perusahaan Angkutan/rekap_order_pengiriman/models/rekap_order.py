from odoo import api, models, fields
from odoo.exceptions import UserError
from datetime import date, datetime

class RekapOrder(models.Model):
	_name = 'rekap.order'
	_description = 'Rekap Order Kirim'
	_rec_name = "kode_rekap"

	company_id = fields.Many2one('res.company', ondelete='cascade', default=lambda self: self.env.user.company_id)
	kode_rekap = fields.Char(required=True, copy=False)
	keterangan = fields.Text(required=True, copy=False)
	tanggal_awal = fields.Date(required=True, copy=False)
	tanggal_akhir = fields.Date(required=True, copy=False)
	customer_id = fields.Many2one("res.partner", ondelete="restrict", required=True)
	jatuh_tempo = fields.Date(required=True, copy=False)
	tipe_order = fields.Selection([
		('do', 'DO'),
		('regular', 'Regular'),
	], default="do", required=True)
	sudah_rekap_ids = fields.One2many("rekap.order.sudah_rekap", "rekap_id", readonly=True)
	belum_rekap_ids = fields.One2many("rekap.order.belum_rekap", "rekap_id", readonly=True)
	total_sudah_rekap = fields.Float(compute="_compute_total_rekap", store=True)
	total_belum_rekap = fields.Float(compute="_compute_total_rekap", store=True)
	total = fields.Float(compute="_compute_total_rekap", store=True)

	@api.onchange('kode_rekap')
	def _check_kode_rekap(self):
		for i in self:
			if i.kode_rekap:
				rekap = self.env['rekap.order'].search([('kode_rekap', '=', i.kode_rekap)], limit=1)
				if rekap:
					raise UserError("Kode Rekap sudah digunakan.")

	def populate_item(self):
		for i in self:
			if i.tanggal_awal and i.tanggal_akhir and i.customer_id and i.kode_rekap:
				order_ids = self.env['order.pengiriman'].search([('jenis_order', '=', i.tipe_order), ('create_date', '>=', datetime.combine(i.tanggal_awal, datetime.min.time())), ('create_date', '<=', datetime.combine(i.tanggal_akhir, datetime.max.time())), ('masuk_rekap', '=', False)])
				values = []
				for order in order_ids:
					setoran_line = self.env['detail.order'].search([('order_pengiriman', '=', order.id)], limit=1)
					if setoran_line and setoran_line.order_setoran.state == 'done':
						values.append((0, 0, {
							'rekap_id': i.id,
							'order_id': order.id,
						}))
				if len(values) > 0:
					i.belum_rekap_ids = values
				else:
					raise UserError("Tidak ada order yang dapat direkap. Pastikan setoran order telah divalidasi.")

	@api.depends("sudah_rekap_ids.subtotal_ongkos", "belum_rekap_ids.subtotal_ongkos")
	def _compute_total_rekap(self):
		for i in self:
			i.total_sudah_rekap = sum([line.subtotal_ongkos for line in i.sudah_rekap_ids])
			i.total_belum_rekap = sum([line.subtotal_ongkos for line in i.belum_rekap_ids])
			i.total = i.total_sudah_rekap + i.total_belum_rekap

class RekapOrderItem(models.Model):
	_name = 'rekap.order.item'
	_description = "Order Rekap Line"

	rekap_id = fields.Many2one("rekap.order", ondelete="cascade", required=True)

	company_id = fields.Many2one('res.company', ondelete='cascade', default=lambda self: self.env.user.company_id)
	active = fields.Boolean(default=True, readonly=True)
	order_id = fields.Many2one("order.pengiriman", ondelete="restrict", required=True, readonly=True)

	tanggal = fields.Datetime(related="order_id.create_date", store=True)
	no_surat_jalan = fields.Char(related="order_id.nomor_surat_jalan", store=True)
	plant = fields.Many2one("konfigurasi.plant", related="order_id.plant", store=True)
	faktur = fields.Many2many("account.move", compute="_get_invoice", store=True)
	nomor_kendaraan = fields.Char(related="order_id.nomor_kendaraan", store=True)
	alamat_muat = fields.Many2one("konfigurasi.lokasi", related="order_id.alamat_muat", store=True)
	alamat_bongkar = fields.Many2one("konfigurasi.lokasi", related="order_id.alamat_bongkar", store=True)

	nama_barang = fields.Text(compute="_get_item_data", store=True)
	subtotal_ongkos = fields.Float(compute="_get_item_data", store=True)

	@api.depends("order_id")
	def _get_item_data(self):
		for i in self:
			if i.order_id:
				if i.order_id.jenis_order == 'do':
					i.nama_barang = "\n".join([line.nama_barang for line in i.order_id.detail_order_do])
				else:
					i.nama_barang = "\n".join([line.nama_barang for line in i.order_id.detail_order_reguler])
				i.subtotal_ongkos = i.order_id.total_ongkos
			else:
				i.nama_barang = ""
				i.subtotal_ongkos = 0

	@api.depends("order_id")
	def _get_invoice(self):
		for i in self:
			if i.order_id:
				detail_order = self.env['detail.order'].sudo().search([('order_pengiriman', '=', i.order_id.id)])
				invoices = self.env['account.move'].sudo().search([('nomor_setoran', '=', detail_order.order_setoran.kode_order_setoran), ('move_type', '=', 'out_invoice')])
				i.faktur = [(6, 0, invoices.ids)]
			else:
				i.faktur = [(5, 0 ,0)]

class RekapOrderSudah(models.Model):
	_name = 'rekap.order.sudah_rekap'
	_inherit = "rekap.order.item"
	_description = "Order Rekap Sudah Rekap"

	inverse_id = fields.Many2one("rekap.order.belum_rekap", ondelete="cascade", readonly=True)

	def toggle_state(self):
		for i in self:
			for invoice in i.faktur:
				if invoice.state == 'posted':
					raise UserError("Tidak dapat mengembalikan rekapan order ini. Order memiliki invoice yang sudah dibayar.")

			if not i.inverse_id:
				i.inverse_id = self.env['rekap.order.belum_rekap'].create({
					'rekap_id': i.rekap_id.id,
					'order_id': i.order_id.id,
					'inverse_id': i.id,
				})
			else:
				i.inverse_id.active = True

			belum_rekap_ids = self.env['rekap.order.belum_rekap'].with_context({'active_test': False}).search([('order_id', '=', i.order_id.id), ('id', '!=', i.inverse_id.id)])
			for belum_rekap in belum_rekap_ids:
				belum_rekap.active = True

			i.order_id.masuk_rekap = False
			i.active = False


class RekapOrderBelum(models.Model):
	_name = 'rekap.order.belum_rekap'
	_inherit = "rekap.order.item"
	_description = "Order Rekap Belum"

	inverse_id = fields.Many2one("rekap.order.sudah_rekap", ondelete="cascade", readonly=True)

	def toggle_state(self):
		for i in self:
			if not i.inverse_id:
				i.inverse_id = self.env['rekap.order.sudah_rekap'].create({
					'rekap_id': i.rekap_id.id,
					'order_id': i.order_id.id,
					'inverse_id': i.id,
				})
			else:
				i.inverse_id.active = True

			belum_rekap_ids = self.env['rekap.order.belum_rekap'].search([('order_id', '=', i.order_id.id), ('id', '!=', i.id)])
			for belum_rekap in belum_rekap_ids:
				belum_rekap.active = False

			i.order_id.masuk_rekap = True
			i.active = False