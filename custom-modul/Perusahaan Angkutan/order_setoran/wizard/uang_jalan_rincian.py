from odoo import api, models, fields
from odoo.exceptions import UserError


class UangJalanRinci(models.TransientModel):
    _name = "uang.jalan.rincian"
    _description = "Rincian Uang Jalan"

    date_from = fields.Date()
    date_to = fields.Date()
    kendaraan = fields.Many2one("fleet.vehicle", ondelete="cascade")

    def open_report(self):
        for i in self:
            if not i.date_from or not i.date_to:
                raise UserError("Belum memasukkan tanggal.")

            uang_jalan = self.env['uang.jalan'].search(
                [('kendaraan', '=', i.kendaraan.id), ('create_date', '>=', i.date_from),
                 ('create_date', '<=', i.date_to)]
            )
            docs = []

            for uj in uang_jalan:
                uang_jalan_name = False
                setoran = self.env['order.setoran'].search([('list_uang_jalan', 'in', [uj.id])])

                if not uj.uang_jalan_nominal_tree and uj.kas_cadangan > 0 and uj.total < 0:
                    values = {
                        'create_date': uj.create_date.strftime("%d %B %Y"),
                        'uang_jalan_name': uj.uang_jalan_name,
                        'sopir': uj.sopir.display_name if uj.sopir else "",
                        'kenek': uj.kenek.display_name if uj.kenek else "",
                        'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                        'sisa_kas_cadangan': uj.sisa_kas_cadangan * -1 if not uang_jalan_name else 0,
                        'biaya_lain': uj.biaya_tambahan * -1,
                        'nominal_uang_jalan': uj.total * -1,
                        'total': uj.total,
                        'muat': False,
                        'bongkar': False,
                        'keterangan': False,
                        'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                    }
                    uang_jalan_name = uj.uang_jalan_name
                    docs.append(values)

                    if uj.state == 'closed':
                        values = {
                            'create_date': uj.create_date.strftime("%d %B %Y"),
                            'uang_jalan_name': uj.uang_jalan_name,
                            'sopir': uj.sopir.display_name if uj.sopir else "",
                            'kenek': uj.kenek.display_name if uj.kenek else "",
                            'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                            'sisa_kas_cadangan': uj.sisa_kas_cadangan if not uang_jalan_name else 0,
                            'biaya_lain': uj.biaya_tambahan,
                            'nominal_uang_jalan': uj.total,
                            'total': uj.total * -1,
                            'muat': False,
                            'bongkar': False,
                            'keterangan': "Kembali Kasbon",
                            'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                        }
                        docs.append(values)

                if not uj.uang_jalan_nominal_tree and uj.kas_cadangan > 0:
                    values = {
                        'create_date': uj.create_date.strftime("%d %B %Y"),
                        'uang_jalan_name': uj.uang_jalan_name,
                        'sopir': uj.sopir.display_name if uj.sopir else "",
                        'kenek': uj.kenek.display_name if uj.kenek else "",
                        'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                        'sisa_kas_cadangan': uj.sisa_kas_cadangan * -1 if not uang_jalan_name else 0,
                        'biaya_lain': uj.biaya_tambahan,
                        'nominal_uang_jalan': 0,
                        'total': uj.sisa_kas_cadangan + uj.kas_cadangan,
                        'muat': False,
                        'bongkar': False,
                        'keterangan': False,
                        'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                    }
                    uang_jalan_name = uj.uang_jalan_name
                    docs.append(values)

                    if uj.state == 'closed':
                        values = {
                            'create_date': uj.create_date.strftime("%d %B %Y"),
                            'uang_jalan_name': uj.uang_jalan_name,
                            'sopir': uj.sopir.display_name if uj.sopir else "",
                            'kenek': uj.kenek.display_name if uj.kenek else "",
                            'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                            'sisa_kas_cadangan': uj.sisa_kas_cadangan * -1 if not uang_jalan_name else 0,
                            'biaya_lain': uj.biaya_tambahan,
                            'nominal_uang_jalan': 0,
                            'total': (uj.sisa_kas_cadangan + uj.kas_cadangan) * -1,
                            'muat': False,
                            'bongkar': False,
                            'keterangan': "Kembali Kasbon",
                            'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                        }
                        docs.append(values)

                elif not uj.uang_jalan_nominal_tree and uj.kas_cadangan == 0:
                    values = {
                        'create_date': uj.create_date.strftime("%d %B %Y"),
                        'uang_jalan_name': uj.uang_jalan_name,
                        'sopir': uj.sopir.display_name if uj.sopir else "",
                        'kenek': uj.kenek.display_name if uj.kenek else "",
                        'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                        'sisa_kas_cadangan': uj.sisa_kas_cadangan * -1 if not uang_jalan_name else 0,
                        'biaya_lain': uj.biaya_tambahan,
                        'nominal_uang_jalan': 0,
                        'total': uj.total,
                        'muat': False,
                        'bongkar': False,
                        'keterangan': False,
                        'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                    }
                    uang_jalan_name = uj.uang_jalan_name
                    docs.append(values)

                    if uj.state == 'closed':
                        values = {
                            'create_date': uj.create_date.strftime("%d %B %Y"),
                            'uang_jalan_name': uj.uang_jalan_name,
                            'sopir': uj.sopir.display_name if uj.sopir else "",
                            'kenek': uj.kenek.display_name if uj.kenek else "",
                            'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                            'sisa_kas_cadangan': uj.sisa_kas_cadangan * -1 if not uang_jalan_name else 0,
                            'biaya_lain': uj.biaya_tambahan * -1,
                            'nominal_uang_jalan': 0 * -1,
                            'total': uj.total * -1,
                            'muat': False,
                            'bongkar': False,
                            'keterangan': "Kembali Kasbon",
                            'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                        }

                        docs.append(values)

                elif uj.uang_jalan_nominal_tree:
                    for line in uj.uang_jalan_nominal_tree:
                        if not uang_jalan_name:
                            total = line.nominal_uang_jalan - uj.sisa_kas_cadangan + uj.kas_cadangan + uj.biaya_tambahan
                        else:
                            total = line.nominal_uang_jalan

                        values = {
                            'create_date': uj.create_date.strftime("%d %B %Y"),
                            'uang_jalan_name': uj.uang_jalan_name,
                            'sopir': uj.sopir.display_name if uj.sopir else "",
                            'kenek': uj.kenek.display_name if uj.kenek else "",
                            'nominal_uang_jalan': line.nominal_uang_jalan,
                            'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                            'sisa_kas_cadangan': uj.sisa_kas_cadangan * -1 if not uang_jalan_name else 0,
                            'biaya_lain': uj.biaya_tambahan,
                            'total': total,
                            'muat': line.muat.display_name,
                            'bongkar': line.bongkar.display_name,
                            'keterangan': line.keterangan,
                            'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                        }

                        uang_jalan_name = uj.uang_jalan_name
                        docs.append(values)

                        if uj.state == 'closed':
                            values = {
                                'create_date': uj.create_date.strftime("%d %B %Y"),
                                'uang_jalan_name': uj.uang_jalan_name,
                                'sopir': uj.sopir.display_name if uj.sopir else "",
                                'kenek': uj.kenek.display_name if uj.kenek else "",
                                'nominal_uang_jalan': line.nominal_uang_jalan,
                                'kas_cadangan': uj.kas_cadangan if not uang_jalan_name else 0,
                                'sisa_kas_cadangan': uj.sisa_kas_cadangan * -1 if not uang_jalan_name else 0,
                                'biaya_lain': uj.biaya_tambahan,
                                'total': total * -1,
                                'muat': line.muat.display_name,
                                'bongkar': line.bongkar.display_name,
                                'keterangan': "Kembali Kasbon",
                                'setoran': ", ".join([s.display_name for s in setoran]) if setoran else " "
                            }

                            docs.append(values)

            data = {
                'doc_ids': uang_jalan.ids,
                'doc_model': 'uang.jalan',
                'data': docs,
                'kendaraan': i.kendaraan.license_plate,
                'date_from': i.date_from,
                'date_to': i.date_to,
            }

            return self.env.ref('order_setoran.report_uang_jalan_rincian').report_action([], data=data)
