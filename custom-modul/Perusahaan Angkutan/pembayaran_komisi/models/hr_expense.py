from odoo import api, models, fields
from odoo.exceptions import UserError

class HrExpense(models.Model):
	_inherit = "hr.expense"

	bayar_komisi_id = fields.Many2one("bayar.komisi", ondelete="cascade", readonly=True)
	tabung_komisi_id = fields.Many2one("tabung.komisi", ondelete="cascade", readonly=True)

class HrExpenseSheet(models.Model):
	_inherit = "hr.expense.sheet"

	def write(self, values):
		res = super(HrExpenseSheet, self).write(values)
		for rec in self:
			if rec.state == 'done':
				for expense in rec.expense_line_ids:
					komisi = expense.bayar_komisi_id if expense.bayar_komisi_id else False
					if komisi:
						komisi.state = 'dibayar'
						if not komisi.ptu_line_id: 
							komisi.ptu_line_id = self.env['hr.employee.ptu_line'].create({
								'employee_id': komisi.employee_id.id,
								'tipe': 'pengeluaran',
								'nominal': expense.total_amount,
								'state': 'diproses',
							}).id
						komisi.ptu_line_id.state = 'diproses'
						
					komisi = expense.tabung_komisi_id if expense.tabung_komisi_id else False
					if komisi:
						komisi.state = 'dibayar'
						if not komisi.ptu_line_id:
							komisi.ptu_line_id = self.env['hr.employee.ptu_line'].create({
							'employee_id': komisi.employee_id.id,
							'tipe': 'pengeluaran',
							'nominal': expense.total_amount,
							'state': 'diproses',
						}).id
						komisi.ptu_line_id.state = 'diproses'
		return res