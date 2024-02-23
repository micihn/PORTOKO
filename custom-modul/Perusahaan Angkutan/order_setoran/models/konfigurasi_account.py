from odoo import models, api, fields

class KonfigurasiAccountSetoran(models.Model):
    _name = 'konfigurasi.account.setoran'
    _description = 'Konfigurasi Account Setoran'
    _rec_name = 'name'

    name = fields.Char(default="Konfigurasi Account Setoran")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    account_kas = fields.Many2one('account.account', 'Account Cash/Bank')
    account_piutang = fields.Many2one('account.account', 'Account Piutang Uang Jalan')
    account_biaya_ujt = fields.Many2one('account.account', 'Account Biaya UJT')
    journal_setoran = fields.Many2one('account.journal', 'Journal Setoran')
