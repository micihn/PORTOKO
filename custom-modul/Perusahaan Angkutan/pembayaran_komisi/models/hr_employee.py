from odoo import api, models, fields

class HrEmployee(models.Model):
	_inherit = "hr.employee"

	komisi_tertabung = fields.Float(compute="_compute_ptu", store=True)
	ptu_ids = fields.One2many("hr.employee.ptu_line", "employee_id")
	komisi_pending = fields.Float(compute="_compute_komisi_pending", store=True)
	sejarah_komisi_ids = fields.One2many("hr.employee.komisi.sejarah", "employee_id")

	def view_sejarah_komisi(self):
		for employee in self:
			return {
				'type': 'ir.actions.act_window',
				'name': 'Sejarah Komisi',
				'res_model': 'hr.employee.komisi.sejarah',
				'view_mode': 'tree',
				'domain': [('employee_id', '=', employee.id)]
			}

	def view_sejarah_ptu(self):
		for employee in self:
			return {
				'type': 'ir.actions.act_window',
				'name': 'Sejarah PTU',
				'res_model': 'hr.employee.ptu_line',
				'view_mode': 'tree',
				'domain': [('employee_id', '=', employee.id)]
			}

	@api.depends("sejarah_komisi_ids.state", "sejarah_komisi_ids.nominal")
	def _compute_komisi_pending(self):
		for employee in self:
			total = 0
			total += sum([komisi.nominal for komisi in employee.sejarah_komisi_ids if komisi.state == 'pending'])
			employee.komisi_pending = total 

	@api.depends("ptu_ids.nominal", "ptu_ids.tipe")
	def _compute_ptu(self):
		for employee in self:
			total_tabungan = sum([ptu.nominal for ptu in employee.ptu_ids if ptu.tipe == 'pemasukan'])
			total_klaim = sum([ptu.nominal for ptu in employee.ptu_ids if ptu.tipe == 'pengeluaran'])
			employee.komisi_tertabung = total_tabungan - total_klaim

class HrEmployeeKomisiSejarah(models.Model):
	_name = "hr.employee.komisi.sejarah"
	_description = "Sejarah Komisi Karyawan"
	_order = "id desc"
	_rec_name = "setoran_id"

	employee_id = fields.Many2one("hr.employee", ondelete="cascade", required=True)
	nominal = fields.Float(required=True)
	setoran_id = fields.Many2one("order.setoran", ondelete="set null")
	state = fields.Selection([
		('pending', 'Pending'),
		('diproses', 'Diproses'),
	], required=True, default="pending")

class HrEmployeePTULine(models.Model):
	_name = "hr.employee.ptu_line"
	_description = "Sejarah PTU"
	_order = "id desc"

	employee_id = fields.Many2one("hr.employee", ondelete="cascade", required=True)
	nominal = fields.Float(required=True)
	tipe = fields.Selection([
		('pemasukan', 'Pemasukan'),
		('pengeluaran', 'Pengeluaran')
	], required="pemasukan")
	state = fields.Selection([
		('pending', 'Pending'),
		('diproses', 'Diproses'),
	], required=True, default="pending")