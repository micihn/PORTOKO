from odoo import api, models, fields

class OrderSetoran(models.Model):
	_inherit = "order.setoran"

	komisi_sopir_id = fields.Many2one("hr.employee.komisi.sejarah", ondelete="set null", readonly=True)
	komisi_kenek_id = fields.Many2one("hr.employee.komisi.sejarah", ondelete="set null", readonly=True)

	def validate(self):
		for rec in self:
			# Buat sejarah komisi
			if rec.komisi_sopir > 0 and not rec.komisi_sopir_id:
				rec.komisi_sopir_id =  self.env['hr.employee.komisi.sejarah'].create({
					'employee_id': rec.sopir.id,
					'nominal': rec.komisi_sopir,
					'setoran_id': rec.id,
					'state': 'pending',
				}).id
			if rec.komisi_kenek > 0 and not rec.komisi_kenek_id:
				rec.komisi_kenek_id = self.env['hr.employee.komisi.sejarah'].create({
					'employee_id': rec.kenek.id,
					'nominal': rec.komisi_kenek,
					'setoran_id': rec.id,
					'state': 'pending',
				}).id
			return super(OrderSetoran, self).validate()