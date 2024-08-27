from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class CloseUangJalan(models.TransientModel):
	_name = 'uang.jalan.close'
	_description = 'Close Uang Jalan'

	nominal_close = fields.Float('Saldo Yang Digunakan', default=0, digits=(6, 0), required=True)
	order_pengiriman = fields.Many2one('order.pengiriman')
	tanggal_penggunaan = fields.Date(required=True)
	specific_order_pengiriman = fields.Boolean()
	can_use_all_balance_wizard = fields.Boolean()
	keterangan = fields.Text()

	def close_uang_jalan(self):
		for record in self.env['uang.jalan'].browse(self._context.get('active_ids', [])):
			if self.nominal_close < 0 :
				raise ValidationError("Nominal Close uang jalan tidak boleh kurang dari 0 Rupiah")

			if self.nominal_close > 0:
				order_ids = []
				for order_pengiriman in record.uang_jalan_line.order_pengiriman:
					order_ids.append(order_pengiriman.id)

				if self.specific_order_pengiriman == True and self.order_pengiriman.id not in order_ids:
					raise ValidationError('Order Pengiriman Terpilih tidak merupakan bagian dari Surat Jalan')

				if record.balance_uang_jalan < self.nominal_close:
					account_settings = self.env['konfigurasi.account.uang.jalan'].search([('company_id', '=', record.company_id.id)])
					account_uang_jalan = account_settings.account_uang_jalan
					journal_uang_jalan = account_settings.journal_uang_jalan
					account_kas = account_settings.account_kas

					self.env['uang.jalan.balance.history'].create({
						'uang_jalan_id': record.id,
						'company_id': record.company_id.id,
						'keterangan': "Penggunaan Saldo Uang Jalan Di luar nominal yang diberikan",
						'tanggal_pencatatan': self.tanggal_penggunaan,
						'nominal_close': self.nominal_close * -1,
					})

					journal_entry = self.env['account.move'].create({
						'company_id': record.company_id.id,
						'move_type': 'entry',
						'journal_id': journal_uang_jalan.id,
						'date': record.create_date,
						'ref': record.uang_jalan_name,
						'line_ids': [
							(0, 0, {
								'name': record.uang_jalan_name,
								'date': record.create_date,
								'account_id': account_kas.id,
								'company_id': record.company_id.id,
								'credit': self.nominal_close,
							}),

							(0, 0, {
								'name': record.uang_jalan_name,
								'date': record.create_date,
								'account_id': account_uang_jalan.id,
								'company_id': record.company_id.id,
								'debit': self.nominal_close,
							}),
						],
					})

					journal_entry.action_post()

					record.kendaraan.kas_gantung_vehicle -= self.nominal_close

					record.write({
						'state': 'closed',
						'nomor_uang_jalan_selesai': self.env['ir.sequence'].next_by_code('uang.jalan.tutup'),
						'tanggal_tutup': date.today(),
						'keterangan_tutup': self.keterangan
					})

				else:
					if self.specific_order_pengiriman:
						self.env['uang.jalan.balance.history'].create({
							'uang_jalan_id': record.id,
							'company_id': record.company_id.id,
							'keterangan': "Penggunaan Saldo Uang Jalan Untuk " + str(self.order_pengiriman.order_pengiriman_name),
							'tanggal_pencatatan': self.tanggal_penggunaan,
							'nominal_close': self.nominal_close * -1,
						})
					else:
						self.env['uang.jalan.balance.history'].create({
							'uang_jalan_id': record.id,
							'company_id': record.company_id.id,
							'keterangan': "Penggunaan Saldo Uang Jalan Untuk Seluruh Order Pengiriman",
							'tanggal_pencatatan': self.tanggal_penggunaan,
							'nominal_close': self.nominal_close * -1,
						})

					record.can_use_all_balance = False

					record.kendaraan.kas_gantung_vehicle -= self.nominal_close

					record.write({
						'state': 'closed',
						'nomor_uang_jalan_selesai': self.env['ir.sequence'].next_by_code('uang.jalan.tutup'),
						'tanggal_tutup': date.today(),
						'keterangan_tutup': self.keterangan
					})

			elif self.nominal_close == 0:
				account_settings = self.env['konfigurasi.account.uang.jalan'].search([('company_id', '=', record.company_id.id)])
				account_uang_jalan = account_settings.account_uang_jalan
				journal_uang_jalan = account_settings.journal_uang_jalan
				account_kas = account_settings.account_kas
				balance_uang_jalan = record.balance_uang_jalan

				self.env['uang.jalan.balance.history'].create({
					'uang_jalan_id': record.id,
					'company_id': record.company_id.id,
					'keterangan': "Saldo uang jalan dikembalikan",
					'tanggal_pencatatan': self.tanggal_penggunaan,
					'nominal_close': balance_uang_jalan * -1,
				})

				journal_entry = self.env['account.move'].create({
					'company_id': record.company_id.id,
					'move_type': 'entry',
					'journal_id': journal_uang_jalan.id,
					'date': record.create_date,
					'ref': record.uang_jalan_name,
					'line_ids': [
						(0, 0, {
							'name': record.uang_jalan_name,
							'date': self.tanggal_penggunaan,
							'account_id': account_uang_jalan.id,
							'company_id': record.company_id.id,
							'credit': balance_uang_jalan,
						}),

						(0, 0, {
							'name': record.uang_jalan_name,
							'date': self.tanggal_penggunaan,
							'account_id': account_kas.id,
							'company_id': record.company_id.id,
							'debit': balance_uang_jalan,
						}),
					],
				})

				journal_entry.action_post()

				record.kendaraan.kas_gantung_vehicle -= balance_uang_jalan

				record.write({
					'state': 'closed',
					'nomor_uang_jalan_selesai': self.env['ir.sequence'].next_by_code('uang.jalan.tutup'),
					'tanggal_tutup': date.today(),
					'keterangan_tutup': self.keterangan
				})

