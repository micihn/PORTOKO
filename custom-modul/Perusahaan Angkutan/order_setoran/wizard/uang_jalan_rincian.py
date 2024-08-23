from odoo import api, models, fields
from odoo.exceptions import UserError

class UangJalanRinci(models.TransientModel):
	_name = "uang.jalan.rincian"
	_description = "Rincian Uang Jalan"

	date_from = fields.Date()
	date_to = fields.Date()
	kendaraan = fields.Many2one("fleet.vehicle", ondelete="cascade")

	def open_report(self):
		for i in self:
			if not i.date_from or not i.date_to:
				raise UserError("Belum memasukkan tanggal.")

			uang_jalan = self.env['uang.jalan'].search([('kendaraan', '=', i.kendaraan.id), ('create_date', '>=', i.date_from), ('create_date', '<=', i.date_to)])
			docs = []

			for uj in uang_jalan:
				uang_jalan_name = False
				setoran = self.env['order.setoran'].search([('list_uang_jalan', 'in', [uj.id])])

				for line in uj.uang_jalan_nominal_tree:
					values = {}
					values['create_date'] = uj.create_date.strftime("%d %B %Y")
					values['uang_jalan_name'] = uj.uang_jalan_name
					values['sopir'] = uj.sopir.display_name if uj.sopir else ""
					values['kenek'] = uj.kenek.display_name if uj.kenek else ""
					values['nominal_uang_jalan'] = line.nominal_uang_jalan
					values['kas_cadangan'] = uj.kas_cadangan if uang_jalan_name == False else 0
					values['sisa_kas_cadangan'] = uj.sisa_kas_cadangan * -1 if uang_jalan_name == False else 0
					values['biaya_lain'] = uj.biaya_tambahan
					values['total'] = line.nominal_uang_jalan - uj.sisa_kas_cadangan + uj.kas_cadangan + uj.biaya_tambahan if uang_jalan_name == False else line.nominal_uang_jalan
					values['muat'] = line.muat.display_name
					values['bongkar'] = line.bongkar.display_name
					values['keterangan'] = line.keterangan

					if setoran:
						values['setoran'] = ", ".join([s.display_name for s in setoran])
					else:
						values['setoran'] = " "

					uang_jalan_name = uj.uang_jalan_name
					docs.append(values)

			data = {
				'doc_ids': uang_jalan.ids,
				'doc_model': 'uang.jalan',
				'data': docs,
				'kendaraan': i.kendaraan.license_plate,
				'date_from': i.date_from,
				'date_to': i.date_to,
			}

			return self.env.ref('order_setoran.report_uang_jalan_rincian').report_action([], data=data)
