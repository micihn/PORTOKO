from odoo import models, api, fields

class KonfigurasiPenjualanPTU(models.Model):
    _name = 'konfigurasi.penjualan.ptu'
    _description = 'Konfigurasi Penjualan PTU'

    name = fields.Char()
    company_id = fields.Many2one("res.company", ondelete="cascade", default=lambda self: self.env.company)
    journal_sparepart  = fields.Many2one('account.journal', string="Journal Sparepart")
    account_piutang_komisi = fields.Many2one('account.account', string="Piutang Komisi")
    account_persediaan_sparepart = fields.Many2one('account.account', string="Persediaan Sparepart")