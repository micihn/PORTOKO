from odoo import fields, api, models

class KonfigurasiKomisi(models.Model):
    _name = 'konfigurasi.komisi'
    _description = 'Konfigurasi Komisi'

    name = fields.Char()
    company_id = fields.Many2one("res.company", ondelete="cascade", default=lambda self: self.env.company)
    journal_komisi = fields.Many2one('account.journal', string="Journal Komisi")
    account_komisi = fields.Many2one('account.account', string="Account Komisi")
    account_cash = fields.Many2one('account.account', string="Account Cash/Bank")
