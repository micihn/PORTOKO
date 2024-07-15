from odoo import api, models, fields, exceptions

class UangJalanRinci(models.TransientModel):
	_name = "uang.jalan.rincian"
	_description = "Rincian Uang Jalan"

	date_from = fields.Date()
	date_to = fields.Date()
	kendaraan = fields.Many2one("fleet.vehicle", ondelete="cascade")

	def open_report(self):
		for i in self:
			if not i.date_from or not i.date_to:
				raise exceptions.UserError("Belum memasukkan tanggal.")

			uang_jalan = self.env['uang.jalan'].search([('kendaraan', '=', i.kendaraan.id), ('create_date', '>=', i.date_from), ('create_date', '<=', i.date_to)])
			docs = []

			for uj in uang_jalan:
				values = {
					'create_date': "",
					'uang_jalan_name': "",
					'sopir': "",
					'kenek': "",
					'nominal_uang_jalan': 0,
					'sisa_kas_cadangan': 0,
					'kas_cadangan': 0,
					'biaya_lain': 0,
					'total': 0,
					'setoran': "",
					'muat': "",
					'bongkar': "",
					'keterangan': "",
				}

				# Get setoran
				setoran = self.env['order.setoran'].search([('relatable_uang_jalan', 'in', [uj.id])])
				if setoran:
					values['setoran'] = ", ".join([s.display_name for s in setoran])

				# Get sisa_kas_cadangan
				prev_uj = self.env['uang.jalan'].search([('id', '<', uj.id), ('kendaraan', '=', uj.kendaraan.id)], limit=1, order="id desc")
				sisa_kas_cadangan = 0
				if prev_uj:
					sisa_kas_cadangan = -(prev_uj.kas_cadangan)

				if uj.tipe_uang_jalan == 'standar':
					for line in uj.uang_jalan_line:
						values.update({
							'create_date': uj.create_date.strftime("%d %B %Y"),
							'uang_jalan_name': uj.uang_jalan_name,
							'sopir': uj.sopir.display_name if uj.sopir else "",
							'kenek': uj.kenek.display_name if uj.kenek else "",
							'nominal_uang_jalan': line.nominal_uang_jalan,
							'sisa_kas_cadangan': sisa_kas_cadangan,
							'kas_cadangan': uj.kas_cadangan,
							'biaya_lain': uj.biaya_tambahan,
							'total': line.nominal_uang_jalan + sisa_kas_cadangan + uj.kas_cadangan + uj.biaya_tambahan,
							'muat': line.muat.display_name if line.muat else "",
							'bongkar': line.bongkar.display_name if line.bongkar else "",
							'keterangan': line.keterangan if line.keterangan else "",
						})
						docs.append(values)
				else:
					for line in uj.uang_jalan_nominal_tree:
						values.update({
							'create_date': uj.create_date.strftime("%d %B %Y"),
							'uang_jalan_name': uj.uang_jalan_name,
							'sopir': uj.sopir.display_name if uj.sopir else "",
							'kenek': uj.kenek.display_name if uj.kenek else "",
							'nominal_uang_jalan': line.nominal_uang_jalan,
							'sisa_kas_cadangan': sisa_kas_cadangan,
							'kas_cadangan': uj.kas_cadangan,
							'biaya_lain': uj.biaya_tambahan,
							'total': line.nominal_uang_jalan + sisa_kas_cadangan + uj.kas_cadangan + uj.biaya_tambahan,
							'muat': line.muat.display_name if line.muat else "",
							'bongkar': line.bongkar.display_name if line.bongkar else "",
							'keterangan': line.keterangan if line.keterangan else "",
						})
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