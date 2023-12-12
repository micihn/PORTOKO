from odoo import api, fields, models

class ConfigurationService(models.Model):
    _name = 'fleet.configuration.service'
    _description = 'Fleet Service Configuration'
    _rec_name = 'name'

    name = fields.Char(readonly=True, default='Fleet Configuration Service')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    operation_type = fields.Many2one('stock.picking.type', string='Operasi Sparepart')
