from odoo import api, fields, models

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    def create_konfigurasi_solar_uang_makan(self, company):
        self.env['konfigurasi.solar.uang.makan'].sudo().create({
            'name': 'Konfigurasi Solar Uang Makan',
            'harga_solar': 0,
            'uang_makan': 0,
            'company_id': company.id,
        })

    def create_tipe_muatan(self, company):
        tipe_muatan = ['Tronton Isi',
                       'Tronton Kosong',
                       'Tronton Dedicated',
                       'Trailer Isi',
                       'Trailer Kosong',
                       'Trailer Dedicated',
                       ]

        for muatan in tipe_muatan:
            self.env['konfigurasi.tipe.muatan'].sudo().create({
                'tipe_muatan': muatan,
                'company_id': company.id,
            })

    def create_sequence(self, company):

        sequence_data = [
            {
                'name' : 'Order Pengiriman Sequence - ',
                'code': 'order.pengiriman.sequence',
                'implementation': 'standard',
                'prefix': 'SO/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },{
                'name' : 'Oper Order Sequence - ',
                'code': 'oper.order.sequence',
                'implementation': 'standard',
                'prefix': 'OP/%(day)s/%(month)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },{
                'name' : 'Uang Jalan Sequence - ',
                'code': 'uang.jalan.sequence',
                'implementation': 'standard',
                'prefix': 'UJ/%(month)s/%(day)s/%(year)s/',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },{
                'name' : 'Konfigurasi Uang Jalan Sequence - ',
                'code': 'konfigurasi.uang.jalan.sequence',
                'implementation': 'standard',
                'prefix': 'KUJ',
                'padding': 3,
                'number_increment': 1,
                'number_next_actual': 1,
            },

        ]

        for data in sequence_data:
            self.env['ir.sequence'].create({
                'name': data['name'] + str(company.name),
                'code': data['code'],
                'implementation': data['implementation'],
                'active': 'True',
                'company_id': company.id,
                'prefix': data['prefix'],
                'padding': data['padding'],
                'number_increment': data['number_increment'],
                'number_next_actual': data['number_next_actual'],
            })


    @api.model
    def create(self, values):
        company = super(ResCompanyInherit, self).create(values)

        self.create_konfigurasi_solar_uang_makan(company)
        self.create_tipe_muatan(company)
        self.create_sequence(company)

        return company
