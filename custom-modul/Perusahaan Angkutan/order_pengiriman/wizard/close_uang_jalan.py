from odoo import models, fields, api

class CloseUangJalan(models.TransientModel):
    _name = 'uang.jalan.close'
    _description = 'Close Uang Jalan'

    nominal_close = fields.Float('Saldo Yang Digunakan', default=0, digits=(6, 0))
    tanggal_penggunaan = fields.Date(required=True)

    def close_uang_jalan(self):
        for record in self.env['uang.jalan'].browse(self._context.get('active_ids', [])):
            self.env['uang.jalan.balance.history'].create({
                'uang_jalan_id': record.id,
                'company_id': record.company_id.id,
                'keterangan': "Penggunaan Saldo Uang Jalan",
                'tanggal_pencatatan': self.tanggal_penggunaan,
                'nominal_close': self.nominal_close * -1,
            })

            if record.balance_uang_jalan == 0:
                record.state = 'closed'
