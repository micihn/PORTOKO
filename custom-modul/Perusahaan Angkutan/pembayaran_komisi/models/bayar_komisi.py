from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError


class BayarKomisi(models.Model):
	_name = "bayar.komisi"
	_description = "Pembayaran Komisi"
	_rec_name = "kode_pembayaran"

	kode_pembayaran = fields.Char(readonly=True)
	employee_id = fields.Many2one("hr.employee", ondelete="cascade", required=True, states={
		'selesai': [('readonly', True)],
		'dibayar': [('readonly', True)]
	})
	saldo = fields.Float(related="employee_id.komisi_tertabung", readonly=True)
	jumlah = fields.Float(required=True, states={
		'selesai': [('readonly', True)],
		'dibayar': [('readonly', True)]
	})
	keterangan = fields.Text(states={
		'selesai': [('readonly', True)],
		'dibayar': [('readonly', True)]
	})
	ptu_line_id = fields.Many2one("hr.employee.ptu_line", ondelete="set null", readonly=True)
	# expense_id = fields.Many2one("hr.expense", ondelete="set null", readonly=True)
	account_move_id = fields.Many2one("account.move", ondelete="set null", readonly=True)
	state = fields.Selection([
		('dibuat', 'Dibuat'),
		('selesai', 'Selesai'),
		('dibayar', 'Dibayar'),
	], default="dibuat")
	company_id = fields.Many2one("res.company", ondelete="cascade",
								 default=lambda self: self.env.context['allowed_company_ids'][0])

	@api.model
	def create(self, vals_list):
		records = super(BayarKomisi, self).create(vals_list)
		for rec in records:
			rec.kode_pembayaran = self.env['ir.sequence'].next_by_code('bayar.komisi') or 'New'
		return records

	# @api.onchange("saldo", "jumlah")
	# def _validate_jumlah(self):
	# 	for rec in self:
	# 		if rec.employee_id and rec.saldo <= 0:
	# 			raise UserError("Saldo PTU karyawan 0.")
	# 		if rec.employee_id and rec.jumlah > rec.saldo:
	# 			raise UserError("Jumlah komisi yang diambil tidak bisa lebih dari saldo tabungan.")

	def action_submit(self):
		for rec in self:
			# if rec.jumlah <= 0:
			# raise UserError("Jumlah tidak bisa kurang atau sama dengan 0.")

			# Ubah staus ptu
			rec.state = 'dibayar'

			# Buat pembayaran
			if not rec.ptu_line_id:
				rec.ptu_line_id = self.env['hr.employee.ptu_line'].create({
					'employee_id': rec.employee_id.id,
					'nominal': rec.jumlah,
					'tipe': 'pengeluaran',
					'state': 'pending',
				}).id

			# if not rec.expense_id:
			# rec.expense_id = self.env['hr.expense'].create({
			# 	'name': 'Pembayaran Komisi %s' % rec.employee_id.display_name,
			# 	'product_id': self.env.ref('pembayaran_komisi.produk_komisi').id,
			# 	'total_amount': rec.jumlah,
			# 	'employee_id': rec.employee_id.id,
			# 	'reference': rec.kode_pembayaran,
			# 	'payment_mode': 'company_account',
			# 	'bayar_komisi_id': rec.id,
			# }).id

			if not rec.account_move_id:
				account_settings = self.env['konfigurasi.komisi'].search([('company_id', '=', self.env.company.id)])
				journal_kas_1 = account_settings.journal_kas_1
				journal_kas_2 = account_settings.journal_kas_2
				account_kas_1 = account_settings.account_kas_1
				account_kas_2 = account_settings.account_kas_2
				hutang_komisi = account_settings.hutang_komisi
				piutang_komisi = account_settings.piutang_komisi
				expense_komisi = account_settings.expense_komisi

				if not journal_kas_1 or not journal_kas_2 or not account_kas_1 or not account_kas_2 or not hutang_komisi or not piutang_komisi or not expense_komisi:
					raise ValidationError("Anda belum melakukan konfigurasi account pada menu Komisi > Konfigurasi.")

				journal_entry_bayar_komisi = self.env['account.move'].sudo().create({
					'company_id': self.env.company.id,
					'move_type': 'entry',
					'date': fields.Datetime.now(),
					'journal_id': journal_kas_2.id,
					'ref': str(self.kode_pembayaran) + str(" - Klaim Komisi " + self.employee_id.name),
					'line_ids': [
						(0, 0, {
							'name': self.kode_pembayaran,
							'date': fields.Datetime.now(),
							'account_id': piutang_komisi.id,
							'company_id': self.env.company.id,
							'debit': rec.jumlah,
						}),

						(0, 0, {
							'name': self.kode_pembayaran,
							'date': fields.Datetime.now(),
							'account_id': account_kas_2.id,
							'company_id': self.env.company.id,
							'credit': rec.jumlah,
						}),
					],
				})
				journal_entry_bayar_komisi.action_post()

# return {
# 	'type': 'ir.actions.act_window',
# 	'res_model': 'hr.expense',
# 	'res_id': rec.expense_id.id,
# 	'view_mode': 'form',
# }
