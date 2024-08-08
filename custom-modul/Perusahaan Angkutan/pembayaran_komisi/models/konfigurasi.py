from odoo import fields, api, models

class KonfigurasiKomisi(models.Model):
    _name = 'konfigurasi.komisi'
    _description = 'Konfigurasi Komisi'

    name = fields.Char()
    company_id = fields.Many2one("res.company", ondelete="cascade", default=lambda self: self.env.company)
    journal_kas_1 = fields.Many2one('account.journal', string="Journal Kas 1")
    journal_kas_2 = fields.Many2one('account.journal', string="Journal Kas 2") # untuk ngeluarin tabungan
    account_kas_1 = fields.Many2one('account.account', string="Account Kas 1")
    account_kas_2 = fields.Many2one('account.account', string="Account Kas 2")
    hutang_komisi = fields.Many2one('account.account', string="Hutang Komisi")
    piutang_komisi = fields.Many2one('account.account', string="Piutang Komisi")
    expense_komisi = fields.Many2one('account.account', string="Expense Komisi")
