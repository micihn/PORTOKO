from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class UangJalan(models.Model):
    _name = 'uang.jalan'
    _description = 'Uang Jalan'
    _inherit = ['mail.thread']
    _rec_name = 'uang_jalan_name'

    active = fields.Boolean('Archive', default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    # Method untuk auto name assignment
    @api.model
    def create(self, vals):
        if vals.get('uang_jalan_name', 'New') == 'New':
            vals['uang_jalan_name'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('uang.jalan.sequence') or 'New'
        result = super(UangJalan, self).create(vals)
        return result

    state = fields.Selection([
        ('to_submit', "To Submit"),
        ('submitted', "Submitted"),
        ('validated', "Validated"),
        ('paid', "Paid"),
        ('cancel', "Cancelled"),
    ], default='to_submit', string="State", hide=True, tracking=True)

    def write(self, vals):
        result = super(UangJalan, self).write(vals)
        for record in self.uang_jalan_line:
            if record.nominal_uang_jalan == 0:
                nominal_uang_jalan = self.env['konfigurasi.uang.jalan'].search([
                    ('tipe_muatan', '=', int(self.tipe_muatan.id)),
                    ('lokasi_muat', '=', int(record.muat.id)),
                    ('lokasi_bongkar', '=', int(record.bongkar.id)),
                    ('company_id', '=', int(self.env.company.id))
                ]).uang_jalan
                if nominal_uang_jalan:
                    record.nominal_uang_jalan = nominal_uang_jalan
            else:
                pass
        return result

    def set_to_draft(self):
        self.state = 'to_submit'

    def submit(self):
        for record in self:
            if bool(record.kendaraan) == False:
                raise ValidationError('Harap isi Kendaraan sebelum mengkonfirmasi!')
            elif bool(record.sopir) == False:
                raise ValidationError('Harap isi Sopir sebelum mengkonfirmasi!')
            elif bool(record.kenek) == False:
                raise ValidationError('Harap isi Kenek sebelum mengkonfirmasi!')
            elif not record.uang_jalan_line:
                raise ValidationError('Anda belum memasukkan nomor Order Pengiriman!')
            elif record.uang_jalan_line:
                for item in record.uang_jalan_line:
                    if item.tipe_muatan == 'none':
                        raise ValidationError('Harap isi kolom tipe muatan pada Detail Uang Jalan!')

        self.state = 'submitted'

    def paid(self):
        for record in self.uang_jalan_line:
            record.sudo().order_pengiriman.write({
                'is_uang_jalan_terbit': True,
                'state': 'dalam_perjalanan',
                'uang_jalan': self.id,
                'kendaraan': self.kendaraan.id,
                'sopir': self.sopir,
                'kenek': self.kenek or None,
                'nomor_kendaraan': self.kendaraan.license_plate,
                'model_kendaraan': self.kendaraan.model_id.name,
            })

            message = "Uang jalan untuk pengiriman ini telah terbit dengan nomor " + str(self.uang_jalan_name)
            record.sudo().order_pengiriman.message_post(body=message)

        self.state = 'paid'

    def cancel(self):
        for record in self.uang_jalan_line:
            record.sudo().order_pengiriman.write({
                'is_uang_jalan_terbit': False,
                'state': 'order_baru',
                'uang_jalan': None,
                'kendaraan': None,
                'sopir': None,
                'kenek': None,
                'nomor_kendaraan': None,
                'model_kendaraan': None,
            })

            message = "Uang jalan nomor " + str(self.uang_jalan_name) + " untuk pengiriman ini dibatalkan."
            record.sudo().order_pengiriman.message_post(body=message)

        self.state = 'cancel'

    def hitung_ulang_nominal_uj(self):
        for record in self.uang_jalan_line:

            nominal_uang_jalan = self.env['konfigurasi.uang.jalan'].sudo().search([
                ('tipe_muatan', '=', int(record.tipe_muatan.id)),
                ('lokasi_muat', '=', int(record.sudo().muat.id)),
                ('lokasi_bongkar', '=', int(record.sudo().bongkar.id)),
                ('company_id', '=', int(record.env.company.id))
            ]).uang_jalan

            if nominal_uang_jalan:
                record.sudo().nominal_uang_jalan = nominal_uang_jalan

    uang_jalan_name = fields.Char(readonly=True, required=True, copy=False, default='New')
    kendaraan = fields.Many2one('fleet.vehicle', 'Kendaraan', copy=True, ondelete='restrict', states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    sopir = fields.Many2one('hr.employee', 'Sopir', copy=True, ondelete='restrict', states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    kenek = fields.Many2one('hr.employee', 'Kenek', copy=True, ondelete='restrict', states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    keterangan = fields.Text('Keterangan', copy=False, states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    uang_jalan_line = fields.One2many('uang.jalan.line', 'uang_jalan', required=True, copy=False, states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    total = fields.Float('Total', compute='_compute_total', digits=(6, 0))
    biaya_tambahan = fields.Float('Biaya Tambahan', default=0, copy=False, digits=(6, 0), states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    def validate(self):
        self.state = 'validated'

    def unlink(self):
        if any(record.state not in ('to_submit', 'cancel') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'Draft' atau 'Cancel'.")

        return super(UangJalan, self).unlink()

    # Method untuk menghitung subtotal ongkos jenis order DO
    @api.depends('uang_jalan_line.nominal_uang_jalan', 'biaya_tambahan')
    def _compute_total(self):
        for record in self:
            uang_jalan_line = record.sudo().uang_jalan_line
            record.total = sum(uang_jalan_line.sudo().mapped('nominal_uang_jalan')) + record.biaya_tambahan

class UangJalanLine(models.Model):
    _name = 'uang.jalan.line'
    _description = 'Uang Jalan Line'

    uang_jalan = fields.Many2one('uang.jalan', invisible=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    tipe_muatan = fields.Many2one('konfigurasi.tipe.muatan', 'Tipe Muatan', required=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order', domain=[('state', '=', 'order_baru')], ondelete='restrict',)
    muat = fields.Many2one('konfigurasi.lokasi', 'Muat', compute='_compute_muat_and_bongkar')
    bongkar = fields.Many2one('konfigurasi.lokasi', 'Bongkar', compute='_compute_muat_and_bongkar')
    keterangan = fields.Text('Keterangan')
    nominal_uang_jalan = fields.Float('Nominal UJ', digits=(6, 0))

    @api.depends('order_pengiriman.alamat_muat', 'order_pengiriman.alamat_bongkar')
    def _compute_muat_and_bongkar(self):
        for record in self:
            record.muat = record.order_pengiriman.alamat_muat
            record.bongkar = record.order_pengiriman.alamat_bongkar

    @api.depends('order_pengiriman')
    def _calculate_nominal_uang_jalan(self):
        nominal_uang_jalan = self.env['konfigurasi.uang.jalan'].search([
            ('tipe_muatan', '=', int(self.tipe_muatan.id)),
            ('lokasi_muat', '=', int(self.muat.id)),
            ('lokasi_bongkar', '=', int(self.bongkar.id)),
            ('company_id', '=', int(self.env.company.id))
        ]).uang_jalan
        if nominal_uang_jalan:
            self.nominal_uang_jalan = nominal_uang_jalan
        else:
            self.nominal_uang_jalan = 0

    @api.onchange('tipe_muatan')
    def _calculate_nominal_uang_jalan_with_tipe_muatan(self):
        if bool(self.tipe_muatan) == False:
            pass
        else:
            nominal_uang_jalan = self.env['konfigurasi.uang.jalan'].search([
                ('tipe_muatan', '=', int(self.tipe_muatan.id)),
                ('lokasi_muat', '=', int(self.muat.id)),
                ('lokasi_bongkar', '=', int(self.bongkar.id)),
                ('company_id', '=', int(self.env.company.id))
            ]).uang_jalan
            if nominal_uang_jalan:
                self.nominal_uang_jalan = nominal_uang_jalan
            else:
                self.nominal_uang_jalan = 0
                self.env.user.notify_warning(message='Konfigurasi Uang Jalan untuk lokasi muat di ' + str(
                    self.muat.lokasi) + ' dan bongkar di ' + str(
                    self.bongkar.lokasi) + ' tidak ditemukan. Harap isi pengaturan di Konfigurasi > Uang Jalan',
                                             sticky=True, title='Konfigurasi Uang Jalan Tidak Ditemukan')


