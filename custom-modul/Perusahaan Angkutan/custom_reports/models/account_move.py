from odoo import api, models, fields, _
from odoo.tools import (
    formatLang,
)

class AccountMove(models.Model):
	_inherit = "account.move"

	@api.depends('move_type', 'line_ids.amount_residual')
	def _compute_payments_widget_reconciled_info(self):
		for move in self:
			payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

			if move.state == 'posted' and move.is_invoice(include_receipts=True):
				reconciled_vals = []
				reconciled_partials = move._get_all_reconciled_invoice_partials()
				for reconciled_partial in reconciled_partials:
					counterpart_line = reconciled_partial['aml']
					if counterpart_line.move_id.ref:
						reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
					else:
						reconciliation_ref = counterpart_line.move_id.name
					if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
						foreign_currency = counterpart_line.currency_id
					else:
						foreign_currency = False

					reconciled_vals.append({
						'name': counterpart_line.name,
						'journal_name': counterpart_line.journal_id.name,
						'amount': reconciled_partial['amount'],
						'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else reconciled_partial['currency'].id,
						'date': counterpart_line.date,
						'partial_id': reconciled_partial['partial_id'],
						'account_payment_id': counterpart_line.payment_id.id,
						'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
						'move_id': counterpart_line.move_id.id,
						'ref': reconciliation_ref,
						# these are necessary for the views to change depending on the values
						'is_exchange': reconciled_partial['is_exchange'],
						'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance), currency_obj=counterpart_line.company_id.currency_id),
						'amount_foreign_currency': foreign_currency and formatLang(self.env, abs(counterpart_line.amount_currency), currency_obj=foreign_currency),
						'bank_dest_name': counterpart_line.payment_id.partner_bank_id.bank_id.name,
						'bank_account_number': counterpart_line.payment_id.partner_bank_id.acc_number,
					})
				payments_widget_vals['content'] = reconciled_vals

			if payments_widget_vals['content']:
				move.invoice_payments_widget = payments_widget_vals
			else:
				move.invoice_payments_widget = False