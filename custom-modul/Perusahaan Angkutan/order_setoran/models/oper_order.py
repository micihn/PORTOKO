from odoo import api, models, fields, exceptions

class OperOrder(models.Model):
    _inherit = 'oper.order'

    @api.model
    def create(self, vals):
        vals['state'] = 'confirmed'
        rec = super(OperOrder, self).create(vals)
        if self._context.get('active_model') == 'oper.setoran':
            active_id = self._context.get('active_id', False)
            if active_id:
                values = self.env['list.oper.order.setoran'].default_get(self.env['list.oper.order.setoran']._fields)
                values.update({
                    'oper_setoran': active_id,
                    'oper_order': rec.id,
                    'jumlah_oper_order': rec.biaya_total,
                })
                self.env['list.oper.order.setoran'].create(values)
        return rec