from odoo import api, fields, models

class ServiceFleetReport(models.TransientModel):
    _name = 'service.fleet.report'
    _description = 'Service Fleet Report Wizard'

    kendaraan = fields.Many2one('fleet.vehicle')
    tanggal_start = fields.Date()
    tanggal_finish = fields.Date()

    def generate_report(self):
        data = {'tanggal_start': self.tanggal_start, 'tanggal_finish': self.tanggal_finish}
        return self.env.ref('fleet_reporting.report_service_fleet_action').report_action([], data=data)