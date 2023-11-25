from odoo import models, api, fields

class KonfigurasiAccount(models.Model):
    _name = 'konfigurasi.account.uang.jalan'
    _description = 'Konfigurasi Account Uang Jalan'
    _rec_name = 'name'

    name = fields.Char(default="Konfigurasi Account Uang Jalan")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    account_uang_jalan = fields.Many2one('account.account', 'Account Uang Jalan')
    account_kas = fields.Many2one('account.account', 'Account Cash/Bank')
