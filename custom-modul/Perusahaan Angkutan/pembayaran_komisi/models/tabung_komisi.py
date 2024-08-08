from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

class TabungKomisi(models.Model):
	_name = "tabung.komisi"
	_description = "Tabung Komisi"
	_rec_name = "kode_ptu"

	kode_ptu = fields.Char(readonly=True)
	employee_id = fields.Many2one("hr.employee", ondelete="cascade", required=True, states={
		'selesai': [('readonly', True)],
		'dibayar': [('readonly', True)]
	})
	komisi_ids = fields.Many2many("hr.employee.komisi.sejarah", string="List Komisi", domain="[('state', '=', 'tersimpan')]", states={
		'selesai': [('readonly', True)],
		'dibayar': [('readonly', True)]
	})
	total_komisi = fields.Float("Total Komisi", compute="_compute_komisi", store=True)
	total_disimpan = fields.Float("PTU", default=0, states={
		'selesai': [('readonly', True)],
		'dibayar': [('readonly', True)]
	})
	jumlah = fields.Float("Jumlah", compute="_compute_komisi", store=True)
	keterangan = fields.Text(states={
		'selesai': [('readonly', True)],
		'dibayar': [('readonly', True)]
	})
	ptu_line_id = fields.Many2one("hr.employee.ptu_line", ondelete="set null", readonly=True)
	expense_id = fields.Many2one("hr.expense", ondelete="set null", readonly=True)
	state = fields.Selection([
		('dibuat', 'Dibuat'),
		('selesai', 'Selesai'),
		('dibayar', 'Dibayar'),
	], default="dibuat")
	company_id = fields.Many2one("res.company", ondelete="cascade", default=lambda self: self.env.company)

	@api.model
	def create(self, vals_list):
		records = super(TabungKomisi, self).create(vals_list)
		for rec in records:
			rec.kode_ptu = self.env['ir.sequence'].next_by_code('tabung.komisi') or 'New'
		return records

	@api.onchange("employee_id")
	def _populate_komisi_list(self):
		for rec in self:
			if rec.employee_id:
				komisi_list = self.env['hr.employee.komisi.sejarah'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'pending')])
				if not komisi_list:
					raise UserError("Tidak ditemukan komisi untuk setoran yang belum dibayar.")
				rec.komisi_ids = [(6, 0, komisi_list.ids)]
			else:
				rec.komisi_ids = [(5, 0, 0)]

	@api.depends("komisi_ids.nominal", "total_disimpan")
	def _compute_komisi(self):
		for rec in self:
			if rec.komisi_ids:
				total = sum([komisi.nominal for komisi in rec.komisi_ids])
				rec.total_komisi = total
				rec.jumlah = total - rec.total_disimpan

	def action_submit(self):
		for rec in self:
			# Ubah status komisi
			for komisi in rec.komisi_ids:
				komisi.state = 'diproses'

			# Ubah staus ptu
			rec.state = 'selesai'

			# Tabung sisanya
			if rec.total_disimpan > 0:
				rec.ptu_line_id = self.env['hr.employee.ptu_line'].create({
					'employee_id': rec.employee_id.id,
					'tipe': 'pemasukan',
					'nominal': rec.total_disimpan,
					'state': 'diproses',
				}).id

				journal_kas_1 = account_settings.journal_kas_1
				journal_kas_2 = account_settings.journal_kas_2
				account_kas_1 = account_settings.account_kas_1
				account_kas_2 = account_settings.account_kas_2
				hutang_komisi = account_settings.hutang_komisi
				piutang_komisi = account_settings.piutang_komisi
				expense_komisi = account_settings.expense_komisi

				if not journal_kas_1 or not journal_kas_2 or not account_kas_1 or not account_kas_2 or not hutang_komisi or not piutang_komisi or not expense_komisi:
					raise ValidationError("Anda belum melakukan konfigurasi account pada menu Komisi > Konfigurasi.")

				# ORM untuk membuat account.move yang berdasarkan Total Komisi
				journal_entry_total_komisi = self.env['account.move'].sudo().create({
					'company_id': self.env.company.id,
					'move_type': 'entry',
					'date': fields.Datetime.now(),
					'journal_id': journal_kas_1.id,
					'ref': str(self.kode_ptu) + str(" - Hutang Komisi " + self.employee_id.name),
					'line_ids': [
						# Account Hutang Komisi
						(0, 0, {
							'name': self.kode_ptu,
							'date': fields.Datetime.now(),
							'account_id': hutang_komisi.id,
							'company_id': self.env.company.id,
							'debit': rec.total_komisi,
						}),

						# Account Kas 1
						(0, 0, {
							'name': self.kode_ptu,
							'date': fields.Datetime.now(),
							'account_id':  account_kas_1.id,
							'company_id': self.env.company.id,
							'credit': rec.total_komisi,
						}),

						# Expense Komisi Supir
						(0, 0, {
							'name': self.kode_ptu,
							'date': fields.Datetime.now(),
							'account_id': expense_komisi.id,
							'company_id': self.env.company.id,
							'debit': rec.total_komisi,
						}),

						# Hutang Komisi
						(0, 0, {
							'name': self.kode_ptu,
							'date': fields.Datetime.now(),
							'account_id': hutang_komisi.id,
							'company_id': self.env.company.id,
							'credit': rec.total_komisi,
						}),
					],
				})
				journal_entry_total_komisi.action_post()

				# ORM Menyimpan uang ke PTU
				journal_entry_ptu = self.env['account.move'].sudo().create({
					'company_id': self.env.company.id,
					'move_type': 'entry',
					'date': fields.Datetime.now(),
					'journal_id': journal_kas_1.id,
					'ref': str(self.kode_ptu) + str(" - PTU Komisi " + self.employee_id.name),
					'line_ids': [
						# Account Hutang Komisi
						(0, 0, {
							'name': self.kode_ptu,
							'date': fields.Datetime.now(),
							'account_id': account_kas_1.id,
							'company_id': self.env.company.id,
							'debit': rec.total_disimpan,
						}),

						# Account Kas 1
						(0, 0, {
							'name': self.kode_ptu,
							'date': fields.Datetime.now(),
							'account_id':  piutang_komisi.id,
							'company_id': self.env.company.id,
							'credit': rec.total_disimpan,
						}),
					],
				})
				journal_entry_ptu.action_post()



			# # Buat pembayaran
			# if rec.jumlah > 0:
			# 	if not rec.expense_id:
			# 		rec.expense_id = self.env['hr.expense'].create({
			# 			'name': 'Pembayaran Komisi %s' % rec.employee_id.display_name,
			# 			'product_id': self.env.ref('pembayaran_komisi.produk_komisi').id,
			# 			'total_amount': rec.jumlah,
			# 			'employee_id': rec.employee_id.id,
			# 			'reference': rec.kode_ptu,
			# 			'payment_mode': 'company_account',
			# 			'tabung_komisi_id': rec.id,
			# 		}).id

				# return {
				# 	'type': 'ir.actions.act_window',
				# 	'res_model': 'hr.expense',
				# 	'res_id': rec.expense_id.id,
				# 	'view_mode': 'form',
				# }