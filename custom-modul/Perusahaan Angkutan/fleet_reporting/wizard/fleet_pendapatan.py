from odoo import api, fields, models

class FleetPendapatan(models.TransientModel):
    _name = 'fleet.pendapatan'
    _description = 'Pendapatan Per Truck Wizard'

    kendaraan_many = fields.Many2many('fleet.vehicle')
    tanggal_start = fields.Date()
    tanggal_finish = fields.Date()
    order_setoran = fields.Many2many('order.setoran')
    semua_kendaraan = fields.Boolean()
    urutkan_kendaraan = fields.Boolean()
    cetak_rincian = fields.Boolean()

    @api.onchange('semua_kendaraan', 'tanggal_start', 'tanggal_finish', 'kendaraan_many')
    def _onchange_filters(self):
        # Cari Semua Kendaraan
        if self.semua_kendaraan and self.tanggal_start and self.tanggal_finish:
            order_setoran = self.env['order.setoran'].search([
                ('tanggal_st', '>=', self.tanggal_start),
                ('tanggal_st', '<=', self.tanggal_finish),
                ('state', '=', 'done'),
            ])

            if order_setoran:
                self.order_setoran = order_setoran.ids
            else:
                # Clear the services field if no records are found
                self.order_setoran = [(5, 0, 0)]

        elif self.kendaraan_many and self.tanggal_start and self.tanggal_finish:
            self.order_setoran = [(5, 0, 0)]

            order_setoran = self.env['order.setoran'].search([
                ('tanggal_st', '>=', self.tanggal_start),
                ('tanggal_st', '<=', self.tanggal_finish),
                ('state', '=', 'done'),
            ])

            if order_setoran:
                ids = []
                for rec in order_setoran:
                    if rec.kendaraan.id in self.kendaraan_many.ids:
                        ids.append((4, rec.id))
                self.order_setoran = ids
        else:
            self.order_setoran = [(5, 0, 0)]


    def generate_report_pendapatan(self):
        # pendapatan_list = []

        kendaraan_list = []
        setoran_list = []
        for record in self.order_setoran:
            if record.kendaraan.id not in kendaraan_list:
                kendaraan_list.append(record.kendaraan.id)

        for kendaraan in kendaraan_list:
            # Set initial variable untuk tiap fields
            hasil_jasa = 0
            pengeluaran = 0
            pembelian = 0
            biaya_fee = 0
            komisi = 0
            total_jumlah = 0
            sparepart = 0

            sparepart_service = self.env['fleet.vehicle.log.services'].search([
                ('vehicle_id','=', kendaraan),
                ('date', '>=', self.tanggal_start),
                ('date', '<=', self.tanggal_finish),
                ('state_record', '=', 'selesai'),
            ])

            for item in sparepart_service:
                sparepart += sparepart_service.total_amount

            for record in self.order_setoran:
                if kendaraan == record.kendaraan.id:
                    nomor_polisi = record.kendaraan.license_plate
                    hasil_jasa += record.total_jumlah
                    pengeluaran += record.total_pengeluaran
                    pembelian += record.total_pembelian
                    biaya_fee += record.total_biaya_fee
                    komisi += record.komisi_kenek + record.komisi_sopir
                    spare_part = sparepart
                    total_jumlah = hasil_jasa - (pengeluaran + pembelian + biaya_fee + komisi + spare_part)

            setoran_dictionary = {
                'nomor_polisi': nomor_polisi,
                'hasil_jasa': hasil_jasa,
                'pengeluaran': pengeluaran,
                'pembelian': pembelian,
                'biaya_fee': biaya_fee,
                'komisi': komisi,
                'spare_part': sparepart,
                'total_jumlah': total_jumlah,
            }

            setoran_list.append(setoran_dictionary)

        sorted_setoran_list = sorted(setoran_list, key=lambda x: x['nomor_polisi'])

        data = {'tanggal_start': self.tanggal_start.strftime('%d-%m-%Y'),
                'tanggal_finish': self.tanggal_finish.strftime('%d-%m-%Y'),
                'setoran_list': setoran_list,
                }

        data_sorted = {'tanggal_start': self.tanggal_start.strftime('%d-%m-%Y'),
                'tanggal_finish': self.tanggal_finish.strftime('%d-%m-%Y'),
                'setoran_list': sorted_setoran_list,
                }

        if bool(data_sorted):
            return self.env.ref('fleet_reporting.report_fleet_pendapatan_action').report_action([], data=data_sorted)
        else:
            return self.env.ref('fleet_reporting.report_fleet_pendapatan_action').report_action([], data=data)

