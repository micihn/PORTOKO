from odoo import models, fields

class AccountMove(models.Model):
	_inherit = "account.move"

	kontra_bon_id = fields.Many2one("kontra.bon", ondelete="set null", string="Kontra Bon", readonly=True, copy=False)