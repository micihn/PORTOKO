from odoo import fields, models, api

class FleetVehicleUangJalan(models.Model):
    _inherit = 'fleet.vehicle'

    kas_gantung_vehicle = fields.Float('Kas Gantung', digits=(6, 0))