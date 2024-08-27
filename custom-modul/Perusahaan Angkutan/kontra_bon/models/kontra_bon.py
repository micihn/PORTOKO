from odoo import models, fields, api, exceptions
from datetime import date, datetime, timedelta

class KontraBon(models.Model):
	_name = "kontra.bon"
	_description = "Kontra Bon"
	_order = 'id desc'

	def _default_invoices(self):
		invoice_ids = self._context.get('active_model') == 'account.move' and self._context.get('active_ids') or []
		partner_id = False # Customer is selected using the first eligible invoice
		invoices = []
		for inv_id in invoice_ids:
			invoice = self.env['account.move'].search([('id', '=', inv_id), ('kontra_bon_id', '=', False)], limit=1)
			if partner_id:
				if invoice and partner_id == invoice.partner_id.id:
					invoices.append((4, inv_id, 0))
			else:
				if invoice:
					partner_id = invoice.partner_id.id
					invoices.append((4, inv_id, 0))
		return invoices

	def _default_partner(self):
		invoice_ids = self._context.get('active_model') == 'account.move' and self._context.get('active_ids') or []
		partner_id = False # Customer is selected using the first eligible invoice
		invoices = []
		for inv_id in invoice_ids:
			invoice = self.env['account.move'].search([('id', '=', inv_id), ('kontra_bon_id', '=', False)], limit=1)
			if invoice:
				partner_id = invoice.partner_id.id
				break
		return partner_id

	company_id = fields.Many2one("res.company", ondelete="set null", default=lambda self: self.env.company)
	name = fields.Char(string="Kode Kontra Bon", readonly=True, copy=False)
	partner_id = fields.Many2one("res.partner", ondelete="restrict", copy=False, default=_default_partner)
	due_date = fields.Date(string="Jatuh Tempo", required=True, copy=False, default=lambda *a: date.today() + timedelta(days=3))
	invoice_ids = fields.Many2many("account.move", string="Rekapan Faktur", default=_default_invoices, domain="[('move_type', '=', 'out_invoice'), ('kontra_bon_id', '=', False), ('partner_id', '=', partner_id)]")

	_sql_constraints = [('unique_name', 'unique(name)', 'Kode Kontra Bon Harus Unik')]

	@api.model_create_multi
	def create(self, vals_list):
		for val in vals_list:
			val['name'] = self.env['ir.sequence'].next_by_code('kontra.bon') or 'New'
		records = super(KontraBon, self).create(vals_list)
		for rec in records:
			rec._assign_invoice_link()
		return records

	def write(self, values):
		if 'invoice_ids' in values:
			for rec in self:
				current_invoice_ids = rec.invoice_ids.ids
				next_invoice_ids = values['invoice_ids'][0][2]
				if len(current_invoice_ids) > len(next_invoice_ids): # Invoice removal is happening
					# Reset the removed invoice kontra_bon_id
					rec._unassign_invoice_link(current_invoice_ids, next_invoice_ids)
		records = super(KontraBon, self).write(values)
		for rec in self:
			rec._assign_invoice_link()
		return records

	# Assign kontra_bon_id to each invoices
	def _assign_invoice_link(self):
		for bon in self:
			for invoice in bon.invoice_ids:
				invoice.kontra_bon_id = bon.id

	def _unassign_invoice_link(self, current_invoices, next_invoices):
		for bon in self:
			for invoice in bon.invoice_ids:
				if invoice.id in current_invoices and invoice.id not in next_invoices:
					invoice.kontra_bon_id = False