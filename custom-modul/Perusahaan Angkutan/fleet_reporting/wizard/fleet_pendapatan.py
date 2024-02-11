from odoo import api, fields, models

class FleetPendapatan(models.TransientModel):
    _name = 'fleet.pendapatan'
    _description = 'Pendapatan Per Truck Wizard'

    kendaraan = fields.Many2one('fleet.vehicle')
    tanggal_start = fields.Date()
    tanggal_finish = fields.Date()
    order_setoran = fields.Many2many('order.setoran')
    semua_kendaraan = fields.Boolean()
    urutkan_kendaraan = fields.Boolean()
    cetak_rincian = fields.Boolean()

    @api.onchange('semua_kendaraan', 'tanggal_start', 'tanggal_finish')
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
        else:
            # Clear the services field if any of the required fields is not set
            self.order_setoran = [(5, 0, 0)]

    def generate_report_pendapatan(self):
        # pendapatan_list = []

        kendaraan_list = []
        setoran_list = []
        for record in self.order_setoran:
            if record.kendaraan.id not in kendaraan_list:
                kendaraan_list.append(record.kendaraan.id)

        for kendaraan in kendaraan_list:
            hasil_jasa = 0
            pengeluaran = 0
            pembelian = 0
            biaya_fee = 0
            komisi = 0
            total_jumlah = 0
            for record in self.order_setoran:
                if kendaraan == record.kendaraan.id:
                    nomor_polisi = record.kendaraan.license_plate
                    hasil_jasa += record.total_jumlah
                    pengeluaran += record.total_pengeluaran
                    pembelian += record.total_pembelian
                    biaya_fee += record.total_biaya_fee
                    komisi += record.komisi_kenek + record.komisi_sopir
                    total_jumlah = hasil_jasa - (pengeluaran + pembelian + biaya_fee + komisi)

            setoran_dictionary = {
                'nomor_polisi': nomor_polisi,
                'hasil_jasa': hasil_jasa,
                'pengeluaran': pengeluaran,
                'pembelian': pembelian,
                'biaya_fee': biaya_fee,
                'komisi': komisi,
                'total_jumlah': total_jumlah,
            }

            setoran_list.append(setoran_dictionary)

        data = {'tanggal_start': self.tanggal_start.strftime('%d-%m-%Y'),
                'tanggal_finish': self.tanggal_finish.strftime('%d-%m-%Y'),
                'setoran_list': setoran_list,
                }
        return self.env.ref('fleet_reporting.report_fleet_pendapatan_action').report_action([], data=data)

