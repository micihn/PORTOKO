from odoo import api, fields, models

class UangJalanGantung(models.TransientModel):
    _name = 'uang.jalan.gantung'
    _description = 'Uang Jalan Gantung'

    tanggal_start = fields.Date()
    tanggal_finish = fields.Date()
    uang_jalan_tree = fields.Many2many('uang.jalan', 'uj_list')

    @api.onchange('tanggal_start', 'tanggal_finish')
    def _onchange_filters(self):
        if self.tanggal_start and self.tanggal_finish:
            uang_jalan = self.env['uang.jalan'].search([
                ('create_date', '>=', self.tanggal_start),
                ('create_date', '<=', self.tanggal_finish),
                ('balance_uang_jalan', '>', 0),
            ])

            if uang_jalan:
                self.uang_jalan_tree = uang_jalan.ids
            else:
                # Clear the services field if no records are found
                self.uang_jalan_tree = [(5, 0, 0)]
        else:
            # Clear the services field if any of the required fields is not set
            self.uang_jalan_tree = [(5, 0, 0)]

    def generate_report(self):
        uj_list_unsorted = []
        for record in self.uang_jalan_tree:
            uj_dictionary = {
            'nomor_polisi': record.kendaraan.license_plate,
            'nomor_uj': record.uang_jalan_name,
            'tanggal_uj': record.create_date,
            'nominal': record.balance_uang_jalan,
            }

            uj_list_unsorted.append(uj_dictionary)

        uj_list = sorted(uj_list_unsorted, key=lambda x: x['tanggal_uj'], reverse=True)

        data = {'tanggal_start': self.tanggal_start.strftime('%d-%m-%Y'),
                'tanggal_finish': self.tanggal_finish.strftime('%d-%m-%Y'),
                'uj_list': uj_list,
                }
        return self.env.ref('order_pengiriman.report_uang_jalan_gantung_rep').report_action([], data=data)