from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CloseUangJalan(models.TransientModel):
    _name = 'uang.jalan.close'
    _description = 'Close Uang Jalan'

    nominal_close = fields.Float('Saldo Yang Digunakan', default=0, digits=(6, 0), required=True)
    order_pengiriman = fields.Many2one('order.pengiriman')
    tanggal_penggunaan = fields.Date(required=True)
    specific_order_pengiriman = fields.Boolean()
    can_use_all_balance_wizard = fields.Boolean()

    def close_uang_jalan(self):
        for record in self.env['uang.jalan'].browse(self._context.get('active_ids', [])):
            order_ids = []
            for order_pengiriman in record.uang_jalan_line.order_pengiriman:
                order_ids.append(order_pengiriman.id)

            if self.specific_order_pengiriman == True and self.order_pengiriman.id not in order_ids:
                raise ValidationError('Order Pengiriman Terpilih tidak merupakan bagian dari Surat Jalan')

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

