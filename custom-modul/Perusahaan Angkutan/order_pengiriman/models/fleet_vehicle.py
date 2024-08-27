from odoo import fields, models, api

class FleetVehicleUangJalan(models.Model):
    _inherit = 'fleet.vehicle'

    sopir_id = fields.Many2one('hr.employee', string="Sopir")
    kenek_id = fields.Many2one('hr.employee', string="Kenek")
    kas_gantung_vehicle = fields.Float('Kas Gantung', digits=(6, 0))
    kas_cadangan = fields.Float('Kas Cadangan', digits=(6, 0))

