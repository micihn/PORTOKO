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
                ('state_record', '=', 'selesai'),
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
        service_list_unsorted = []
        for record in self.services:
            if record.service_type_id.category == 'service':
                service_dictionary = {
                    'service_category': record.service_type_id.category,
                    'description': record.description,
                    'service_type_id': record.service_type_id.name,
                    'date': record.date.strftime('%d/%m/%Y'),
                    'amount': record.amount,
                    # 'default_code': record.product_id.default_code,
                    # 'name': record.product_id.name,
                    'qty': 1,
                    'total_amount': record.total_amount,
                }
            elif record.service_type_id.category == 'sparepart':
                service_dictionary = {
                    'service_category': record.service_type_id.category,
                    'description': record.description,
                    'service_type_id': record.service_type_id.name,
                    'date': record.date.strftime('%d/%m/%Y'),
                }

                items = []
                for item in record.list_sparepart:
                    if item.product_qty != 0:
                        item_dict = {
                            'product_name': item.product_id.name,
                            'product_qty': item.product_qty,
                            'product_cost': item.cost,
                            'product_total_cost': item.total_cost,
                            'product_barcode': item.product_id.default_code,
                        }

                        items.append(item_dict)

                service_dictionary['items'] = items

            service_list_unsorted.append(service_dictionary)

        service_list = sorted(service_list_unsorted, key=lambda x: x['date'], reverse=True)

        data = {'tanggal_start': self.tanggal_start.strftime('%d-%m-%Y'),
                'tanggal_finish': self.tanggal_finish.strftime('%d-%m-%Y'),
                'kendaraan': self.kendaraan.name,
                'license_plate': self.kendaraan.license_plate,
                'services': service_list,
                }
        return self.env.ref('fleet_reporting.report_service_fleet_action').report_action([], data=data)