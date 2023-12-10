from odoo import api, fields, models

class ServiceFleetReport(models.TransientModel):
    _name = 'service.fleet.report'
    _description = 'Service Fleet Report Wizard'

    kendaraan = fields.Many2one('fleet.vehicle')
    tanggal_start = fields.Date()
    tanggal_finish = fields.Date()
    services = fields.Many2many('fleet.vehicle.log.services', 'services_list')

    @api.onchange('kendaraan', 'tanggal_start', 'tanggal_finish')
    def _onchange_filters(self):
        if self.kendaraan and self.tanggal_start and self.tanggal_finish:
            services = self.env['fleet.vehicle.log.services'].search([
                ('vehicle_id', '=', self.kendaraan.id),
                ('date', '>=', self.tanggal_start),
                ('date', '<=', self.tanggal_finish),
            ])

            if services:
                self.services = services.ids
            else:
                # Clear the services field if no records are found
                self.services = [(5, 0, 0)]
        else:
            # Clear the services field if any of the required fields is not set
            self.services = [(5, 0, 0)]

    def generate_report(self):
        data = {'tanggal_start': self.tanggal_start, 'tanggal_finish': self.tanggal_finish, 'services': self.services.ids}
        return self.env.ref('fleet_reporting.report_service_fleet_action').report_action([], data=data)