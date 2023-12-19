from odoo import api, fields, models
from odoo.exceptions import ValidationError
import math

class KonfigurasiUangJalan(models.Model):

    _name = 'konfigurasi.uang.jalan'
    _description = 'Konfigurasi Uang Jalan'
    _inherit = ['mail.thread']
    _rec_name = 'kode_uang_jalan'

    kode_uang_jalan = fields.Char('Kode Uang Jalan', store=True)

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        existing_record = self.search([
            ('tipe_muatan', '=', vals.get('tipe_muatan')),
            ('lokasi_muat', '=', vals.get('lokasi_muat')),
            ('lokasi_bongkar', '=', vals.get('lokasi_bongkar')),
            ('company_id', '=', int(self.env.company.id)),
            ('customer_id', '=', vals.get('customer_id'))
        ])

        if existing_record:
            # Handle the case where a matching record already exists
            # You can raise an exception or handle it as per your business logic
            raise ValidationError("Konfigurasi Uang Jalan yang saat ini anda buat sudah pernah dibuat sebelumnya (" + str(existing_record.kode_uang_jalan)+ "). Harap pastikan kembali Tipe, Lokasi Muat dan Lokasi Bongkar memiliki input yang berbeda")

        # Method untuk auto name assignment
        if vals.get('kode_uang_jalan', 'New') == 'New':
            vals['kode_uang_jalan'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('konfigurasi.uang.jalan.sequence') or 'New'
        result = super(KonfigurasiUangJalan, self).create(vals)
        return result

    def write(self, vals):
        if 'tipe_muatan' in vals or 'lokasi_muat' in vals or 'lokasi_bongkar' in vals or 'customer_id' in vals:
            existing_record = self.search([
                ('tipe_muatan', '=', vals.get('tipe_muatan', self.tipe_muatan.id)),
                ('lokasi_muat', '=', vals.get('lokasi_muat', self.lokasi_muat.id)),
                ('lokasi_bongkar', '=', vals.get('lokasi_bongkar', self.lokasi_bongkar.id)),
                ('company_id', '=', int(self.env.company.id)),
                ('customer_id', '=', vals.get('customer_id', self.customer_id.id))
            ])

            if existing_record:
                # Handle the case where a matching record already exists
                # You can raise an exception or handle it as per your business logic
                raise ValidationError(
                    "Konfigurasi Uang Jalan yang saat ini anda buat sudah pernah dibuat sebelumnya (" + str(
                        existing_record.kode_uang_jalan) + "). Harap pastikan kembali Tipe Muatan, Lokasi Muat dan Lokasi Bongkar memiliki input yang berbeda")

        result = super(KonfigurasiUangJalan, self).write(vals)
        return result

    customer_id = fields.Many2one('res.partner', 'Customer', required=True)
    tipe_muatan = fields.Many2one('konfigurasi.tipe.muatan', 'Tipe Muatan', required=True)
    lokasi_muat = fields.Many2one('konfigurasi.lokasi', 'Lokasi Muat', ondelete='restrict', required=True)
    lokasi_bongkar = fields.Many2one('konfigurasi.lokasi', 'Lokasi Bongkar', ondelete='restrict', required=True)
    jarak = fields.Float('Jarak (Km)', default = 0, required=True)
    solar = fields.Float('Kebutuhan Solar (L)', compute='_calculate_solar')
    uang_solar = fields.Float('Uang Solar', compute='_calculate_uang_solar')
    uang_solar_per_liter = fields.Float('Harga Solar Per Liter', compute='_calculate_uang_solar_per_liter')
    hari = fields.Float('Hari Tempuh')
    uang_makan = fields.Float('Total Uang Makan', compute='_calculate_uang_makan')
    uang_makan_per_hari = fields.Float('Uang Makan Per Hari', compute='_calculate_uang_makan_per_hari')
    kuli = fields.Integer('Biaya Kuli', default=0)
    tol = fields.Integer('Biaya Tol', default=0)
    tonase = fields.Integer('Biaya Tonase', default=0)
    lain_lain = fields.Integer('Biaya Lain-lain', default=0)
    uang_jalan = fields.Float('Uang Jalan', compute='_calculate_uang_jalan')
    uang_jalan_pembulatan = fields.Float('Uang Jalan (Dibulatkan)')

    @api.depends('jarak')
    def _calculate_solar(self):
        for record in self:
            record.solar = record.jarak / 2

    @api.depends('jarak')
    def _calculate_uang_solar_per_liter(self):
        active_uang_solar = self.env['konfigurasi.solar.uang.makan'].search([('company_id', '=', int(self.env.company.id))]).harga_solar
        for record in self:
            record.uang_solar_per_liter = active_uang_solar

    @api.depends('jarak')
    def _calculate_uang_makan_per_hari(self):
        active_uang_makan = self.env['konfigurasi.solar.uang.makan'].search([('company_id', '=', int(self.env.company.id))]).uang_makan
        for record in self:
            record.uang_makan_per_hari = active_uang_makan

    @api.depends('solar', 'uang_solar_per_liter')
    def _calculate_uang_solar(self):
        for record in self:
            record.uang_solar = record.solar * record.uang_solar_per_liter

    @api.onchange('jarak')
    def _calculate_hari(self):
        for record in self:
            if record.jarak <= 99:
                record.hari = 0.5
            elif record.jarak >= 100 and record.jarak <= 199:
                record.hari = 1
            elif record.jarak >= 200 and record.jarak <= 299:
                record.hari = 1.5
            elif record.jarak >= 300 and record.jarak <= 399:
                record.hari = 2
            elif record.jarak >= 400 and record.jarak <= 499:
                record.hari = 2.5
            elif record.jarak >= 500 and record.jarak <= 599:
                record.hari = 3
            elif record.jarak >= 600 and record.jarak <= 699:
                record.hari = 2
            elif record.jarak >= 700 and record.jarak <= 799:
                record.hari = 2
            elif record.jarak >= 800 and record.jarak <= 899:
                record.hari = 2
            else:
                record.hari = 5

    @api.depends('hari', 'uang_makan_per_hari')
    def _calculate_uang_makan(self):
        for record in self:
            record.uang_makan = record.hari * record.uang_makan_per_hari

    @api.depends('uang_makan', 'uang_solar', 'kuli', 'tol', 'tonase', 'lain_lain')
    def _calculate_uang_jalan(self):
        for record in self:
            # record.uang_jalan = math.ceil(record.uang_makan + record.uang_solar + record.kuli + record.tol + record.tonase + record.lain_lain)

            computed_value = record.uang_makan + record.uang_solar + record.kuli + record.tol + record.tonase + record.lain_lain

            # Round up to the nearest multiple of 10,000
            rounded_value = math.ceil(computed_value / 10000) * 10000

            record.uang_jalan = rounded_value