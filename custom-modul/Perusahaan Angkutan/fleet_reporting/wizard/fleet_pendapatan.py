from odoo import api, fields, models
from datetime import datetime

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
        kendaraan_list = []
        setoran_list = []
        # sparepart_rincian = 0
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
                # sparepart_rincian += sparepart_service.total_amount

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

        data = {'tanggal_start': self.tanggal_start.strftime('%d/%m/%Y'),
                'tanggal_finish': self.tanggal_finish.strftime('%d/%m/%Y'),
                'setoran_list': setoran_list,
                }

        data_sorted = {'tanggal_start': self.tanggal_start.strftime('%d/%m/%Y'),
                'tanggal_finish': self.tanggal_finish.strftime('%d/%m/%Y'),
                'setoran_list': sorted_setoran_list,
                }

        if bool(data_sorted):
            if self.cetak_rincian:
                kendaraan_rincian_list = []
                plat_nomer = []
                for record in self.order_setoran:
                    if record.kendaraan.id not in kendaraan_rincian_list:
                        kendaraan_rincian_list.append(record.kendaraan.id)
                        plat_nomer.append(record.kendaraan.license_plate)

                rincian_list = []
                sparepart_list = []
                for kendaraan_rincian in kendaraan_rincian_list:
                    rincian_a = []
                    sparepart_total = 0
                    for setor in self.order_setoran:
                        if kendaraan_rincian == setor.kendaraan.id:
                            rincian = {
                                'tanggal': setor.tanggal_st.strftime('%d/%m/%Y'),
                                'nomor_setoran': setor.kode_order_setoran,
                                'hasil': setor.total_jumlah,
                                'pengeluaran': setor.total_pengeluaran,
                                'pembelian': setor.total_pembelian,
                                'biaya_fee': setor.total_biaya_fee,
                                'komisi': setor.komisi_kenek + setor.komisi_sopir,
                                'jumlah': setor.total_jumlah - setor.total_pengeluaran - setor.total_pembelian - setor.total_biaya_fee - (setor.komisi_kenek + setor.komisi_sopir),
                                'plat_kendaraan': setor.kendaraan.license_plate,
                            }

                            if sparepart_total == 0:
                                sparepart_service = self.env['fleet.vehicle.log.services'].search([
                                    ('vehicle_id', '=', kendaraan_rincian),
                                    ('date', '>=', self.tanggal_start),
                                    ('date', '<=', self.tanggal_finish),
                                    ('state_record', '=', 'selesai'),
                                ])

                                if bool(sparepart_service):
                                    for item in sparepart_service:
                                        sparepart_total += sparepart_service.total_amount
                                else:
                                    sparepart_total = 0

                                # rincian['sparepart_rincian'] = sparepart_total
                                sparepart_list.append(sparepart_total)

                            rincian_a.append(rincian)

                    rincian_list.append(rincian_a)

                data_sorted['rincian'] = rincian_list
                data_sorted['plat_nomer'] = plat_nomer
                data_sorted['sparepart_list'] = sparepart_list

                return self.env.ref('fleet_reporting.report_fleet_pendapatan_action').report_action([], data=data_sorted)
            else:
                return self.env.ref('fleet_reporting.report_fleet_pendapatan_action').report_action([], data=data_sorted)
        else:
            if self.cetak_rincian:
                kendaraan_rincian_list = []
                plat_nomer = []
                for record in self.order_setoran:
                    if record.kendaraan.id not in kendaraan_rincian_list:
                        kendaraan_rincian_list.append(record.kendaraan.id)
                        plat_nomer.append(record.kendaraan.license_plate)

                rincian_list = []
                sparepart_list = []
                for kendaraan_rincian in kendaraan_rincian_list:
                    rincian_a = []
                    sparepart_total = 0
                    for setor in self.order_setoran:
                        if kendaraan_rincian == setor.kendaraan.id:
                            rincian = {
                                'tanggal': setor.tanggal_st.strftime('%d/%m/%Y'),
                                'nomor_setoran': setor.kode_order_setoran,
                                'hasil': setor.total_jumlah,
                                'pengeluaran': setor.total_pengeluaran,
                                'pembelian': setor.total_pembelian,
                                'biaya_fee': setor.total_biaya_fee,
                                'komisi': setor.komisi_kenek + setor.komisi_sopir,
                                'jumlah': setor.total_jumlah - setor.total_pengeluaran - setor.total_pembelian - setor.total_biaya_fee - (setor.komisi_kenek + setor.komisi_sopir),
                                'plat_kendaraan': setor.kendaraan.license_plate,
                            }

                            if sparepart_total == 0:
                                sparepart_service = self.env['fleet.vehicle.log.services'].search([
                                    ('vehicle_id', '=', kendaraan_rincian),
                                    ('date', '>=', self.tanggal_start),
                                    ('date', '<=', self.tanggal_finish),
                                    ('state_record', '=', 'selesai'),
                                ])

                                if bool(sparepart_service):
                                    for item in sparepart_service:
                                        sparepart_total += sparepart_service.total_amount
                                else:
                                    sparepart_total = 0

                                # rincian['sparepart_rincian'] = sparepart_total
                                sparepart_list.append(sparepart_total)

                            rincian_a.append(rincian)

                    rincian_list.append(rincian_a)

                data['rincian'] = rincian_list
                data['plat_nomer'] = plat_nomer
                data['sparepart_list'] = sparepart_list

                return self.env.ref('fleet_reporting.report_fleet_pendapatan_action').report_action([], data=data)
            else:
                return self.env.ref('fleet_reporting.report_fleet_pendapatan_action').report_action([], data=data)
