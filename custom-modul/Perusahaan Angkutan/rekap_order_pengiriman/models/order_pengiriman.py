from odoo import api, models, fields
from odoo.exceptions import UserError

class OrderPengiriman(models.Model):
    _inherit = 'order.pengiriman'

    masuk_rekap = fields.Boolean(readonly=True)