from odoo import api, models, fields, exceptions

class OrderPengiriman(models.Model):
	_inherit = 'order.pengiriman'

	@api.model
	def create(self, vals):
		vals['state'] = 'selesai'
		rec = super(OrderPengiriman, self).create(vals)
		if self._context.get('active_model') == 'oper.setoran':
			active_id = self._context.get('active_id', False)
			if active_id:
				# Create detail setoran
				total = rec.total_biaya_fee + rec.total_biaya_pembelian
				total += (rec.total_ongkos_do if rec.jenis_order == 'do' else rec.total_ongkos_reguler)

				values = self.env['detail.order.setoran'].default_get(self.env['detail.order.setoran']._fields)
				values.update({
					'order_pengiriman': rec.id,
					'tanggal_order': rec.create_date,
					'jenis_order': rec.jenis_order,
					'customer': rec.customer.id,
					'plant': rec.plant.id,
					'nomor_surat_jalan': rec.nomor_surat_jalan,
					'oper_setoran': active_id,
					'jumlah': total,
				})
				self.env['detail.order.setoran'].create(values)

				# Create list pembelian
				values = self.env['list.pembelian.setoran'].default_get(self.env['list.pembelian.setoran']._fields)
				for line in rec.biaya_pembelian:
					values.update({
						'oper_setoran': active_id,
						'order_pengiriman': rec.id,
						'nominal': line.nominal,
					})
					self.env['list.pembelian.setoran'].create(values)

				# Create biaya fee
				values = self.env['biaya.fee.setoran'].default_get(self.env['biaya.fee.setoran']._fields)
				for line in rec.biaya_fee:
					values.update({
						'oper_setoran': active_id,
						'order_pengiriman': rec.id,
						'nominal': line.nominal,
					})
					self.env['biaya.fee.setoran'].create(values)
		return rec