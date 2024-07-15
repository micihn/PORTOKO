from odoo import api, models, fields
from odoo.exceptions import UserError

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

			# Buat pembayaran
			if rec.jumlah > 0:
				if not rec.expense_id:
					rec.expense_id = self.env['hr.expense'].create({
						'name': 'Pembayaran Komisi %s' % rec.employee_id.display_name,
						'product_id': self.env.ref('pembayaran_komisi.produk_komisi').id,
						'total_amount': rec.jumlah,
						'employee_id': rec.employee_id.id,
						'reference': rec.kode_ptu,
						'payment_mode': 'company_account',
						'tabung_komisi_id': rec.id,
					}).id

				return {
					'type': 'ir.actions.act_window',
					'res_model': 'hr.expense',
					'res_id': rec.expense_id.id,
					'view_mode': 'form',
				}