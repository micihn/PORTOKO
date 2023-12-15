from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class UangJalan(models.Model):
    _name = 'uang.jalan'
    _description = 'Uang Jalan'
    _inherit = ['mail.thread']
    _rec_name = 'uang_jalan_name'

    active = fields.Boolean('Archive', default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    tipe_uang_jalan = fields.Selection([
        ('standar', "Standar"),
        ('nominal_saja', "Nominal Saja"),
    ], required=True, default='standar', states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

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

    uang_jalan_nominal_tree = fields.One2many('uang.jalan.nominal.saja', 'uang_jalan_nominal_saja', required=True,
                                              copy=False, states={
            'to_submit': [('readonly', False)],
            'submitted': [('readonly', True)],
            'validated': [('readonly', True)],
            'paid': [('readonly', True)],
        })

    biaya_tambahan_standar = fields.Float('Biaya Tambahan', default=0, copy=False, digits=(6, 0), states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    biaya_tambahan_nominal_saja = fields.Float('Biaya Tambahan', default=0, copy=False, digits=(6, 0), states={
        'to_submit': [('readonly', False)],
        'submitted': [('readonly', True)],
        'validated': [('readonly', True)],
        'paid': [('readonly', True)],
    })

    total_uang_jalan_standar = fields.Float('Total', compute='_compute_total_uang_jalan_standar', default=0, digits=(6, 0))

    state = fields.Selection([
        ('to_submit', "To Submit"),
        ('submitted', "Submitted"),
        ('validated', "Validated"),
        ('paid', "Paid"),
        ('paid_no_order', "Paid, No Order"),
        ('cancel', "Cancelled"),
    ], default='to_submit', string="State", hide=True, tracking=True)

    total_uang_jalan_nominal_saja = fields.Float('Total', compute='_compute_total_nominal_uang_jalan_saja', copy=False, default=0, store=True, digits=(6, 0))
    total = fields.Float('Total', default=0, copy=False, compute='_compute_total', store=True, digits=(6, 0))

    # Method untuk auto name assignment
    @api.model
    def create(self, vals):
        if vals.get('uang_jalan_name', 'New') == 'New':
            vals['uang_jalan_name'] = self.env['ir.sequence'].with_company(self.company_id.id).next_by_code('uang.jalan.sequence') or 'New'
        result = super(UangJalan, self).create(vals)
        return result

    @api.model
    def terbilang(self, bil):
        angka = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam",
                 "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
        Hasil = " "
        n = int(bil)
        if n >= 0 and n <= 11:
            Hasil = angka[n]
        elif n < 20:
            Hasil = self.terbilang(n - 10) + " Belas "
        elif n < 100:
            Hasil = self.terbilang(n / 10) + " Puluh " + self.terbilang(n % 10)
        elif n < 200:
            Hasil = " Seratus " + self.terbilang(n - 100)
        elif n < 1000:
            Hasil = self.terbilang(n / 100) + " Ratus " + self.terbilang(n % 100)
        elif n < 2000:
            Hasil = " Seribu " + self.terbilang(n - 1000)
        elif n < 1000000:
            Hasil = self.terbilang(n / 1000) + " Ribu " + self.terbilang(n % 1000)
        elif n < 1000000000:
            Hasil = self.terbilang(n / 1000000) + " Juta " + self.terbilang(n % 1000000)
        elif n < 1000000000000:
            Hasil = self.terbilang(n / 1000000000) + " Milyar " + self.terbilang(n % 1000000000)
        elif n < 1000000000000000:
            Hasil = self.terbilang(n / 1000000000000) + " Triliyun " + self.terbilang(n % 1000000000000)

        return Hasil


    def write(self, vals):
        if 'tipe_uang_jalan' in vals:
            # Method untuk reset jika transisi "Tipe Uang Jalan" terjadi
            if vals['tipe_uang_jalan'] == 'standar':
                self.biaya_tambahan_nominal_saja = 0
                for record in self.uang_jalan_nominal_tree:
                    record.unlink()
            if vals['tipe_uang_jalan'] == 'nominal_saja':
                self.biaya_tambahan_standar = 0
                for record in self.uang_jalan_line:
                    record.unlink()

        result = super(UangJalan, self).write(vals)

        # Method untuk mencari order pengiriman related
        for record in self.uang_jalan_line:
            if record.nominal_uang_jalan == 0:
                nominal_uang_jalan = self.env['konfigurasi.uang.jalan'].search([
                    ('tipe_muatan', '=', int(record.tipe_muatan.id)),
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
        if self.tipe_uang_jalan == 'standar':
            for record in self:
                if bool(record.kendaraan) == False:
                    raise ValidationError('Harap isi Kendaraan sebelum mengkonfirmasi!')
                elif bool(record.sopir) == False:
                    raise ValidationError('Harap isi Sopir sebelum mengkonfirmasi!')
                elif bool(record.kenek) == False:
                    raise ValidationError('Harap isi Kenek sebelum mengkonfirmasi!')
                elif not record.uang_jalan_line:
                    raise ValidationError('Anda belum memasukkan nomor Order Pengiriman!')

        self.state = 'submitted'

    def paid(self):
        account_settings = self.env['konfigurasi.account.uang.jalan'].search([('company_id', '=', self.company_id.id)])
        account_uang_jalan = account_settings.account_uang_jalan
        account_kas = account_settings.account_kas

        if bool(account_uang_jalan) == False:
            raise ValidationError("Konfigurasi Account belum diisi")

        if bool(account_kas) == False:
            raise ValidationError("Konfigurasi Account belum diisi")

        if self.tipe_uang_jalan == 'standar':

            uang_jalan_list = []
            for rec in self.uang_jalan_line:
                for uang_jalan in rec.sudo().order_pengiriman.uang_jalan:
                    uang_jalan_list.append((6, 0, [uang_jalan.id]))

            for record in self.uang_jalan_line:
                record.sudo().order_pengiriman.write({
                    'is_uang_jalan_terbit': True,
                    'state': 'dalam_perjalanan',
                    'uang_jalan': uang_jalan_list + [(4, self.id, 0)],
                    'kendaraan': self.kendaraan.id,
                    'sopir': self.sopir,
                    'kenek': self.kenek or None,
                    'nomor_kendaraan': self.kendaraan.license_plate,
                    'model_kendaraan': self.kendaraan.model_id.name,
                })

                # Buat Pengurangan Kas Pada Journal Entry

                message = "Uang jalan untuk pengiriman ini telah terbit dengan nomor " + str(self.uang_jalan_name)
                record.sudo().order_pengiriman.message_post(body=message)

            # Buat dan Validate Journal Entry untuk mengurangi nilai pada saldo
            journal_entry = self.env['account.move'].create({
                'company_id': self.company_id.id,
                'move_type': 'entry',
                'date': self.create_date,
                'ref': self.uang_jalan_name,
                'line_ids': [
                    (0, 0, {
                        'name': self.uang_jalan_name,
                        'date': self.create_date,
                        'account_id': account_kas.id,
                        'company_id': self.company_id.id,
                        'credit': self.total,
                    }),

                    (0, 0, {
                        'name': self.uang_jalan_name,
                        'date': self.create_date,
                        'account_id': account_uang_jalan.id,
                        'company_id': self.company_id.id,
                        'debit': self.total,
                    }),
                ],
            })

            journal_entry.action_post()

        elif self.tipe_uang_jalan == 'nominal_saja':
            # Buat dan Validate Journal Entry untuk mengurangi nilai pada saldo
            journal_entry = self.env['account.move'].create({
                'company_id': self.company_id.id,
                'move_type': 'entry',
                'date': self.create_date,
                'ref': self.uang_jalan_name,
                'line_ids': [
                    (0, 0, {
                        'name': self.uang_jalan_name,
                        'date': self.create_date,
                        'account_id': account_kas.id,
                        'company_id': self.company_id.id,
                        'credit': self.total,
                    }),

                    (0, 0, {
                        'name': self.uang_jalan_name,
                        'date': self.create_date,
                        'account_id': account_uang_jalan.id,
                        'company_id': self.company_id.id,
                        'debit': self.total,
                    }),
                ],
            })

            journal_entry.action_post()

        self.state = 'paid'

    def cancel(self):

        uang_jalan_list = []
        for rec in self.uang_jalan_line:
            for uang_jalan in rec.sudo().order_pengiriman.uang_jalan:
                if uang_jalan.id != self.id:
                    uang_jalan_list.append((6, 0, [uang_jalan.id]))
                else:
                    pass

        if self.tipe_uang_jalan == 'standar':
            for record in self.uang_jalan_line:
                record.sudo().order_pengiriman.write({
                    'is_uang_jalan_terbit': False,
                    'state': 'order_baru',
                    'uang_jalan': uang_jalan_list or None,
                    'kendaraan': None,
                    'sopir': None,
                    'kenek': None,
                    'nomor_kendaraan': None,
                    'model_kendaraan': None,
                })

                message = "Uang jalan nomor " + str(self.uang_jalan_name) + " untuk pengiriman ini dibatalkan."
                record.sudo().order_pengiriman.message_post(body=message)

        # Batalkan journal entry pembuatan advanced pihut (Jika ada)
        if self.state == 'paid':
            for record in self.env['account.move'].search([('ref', '=', str(self.uang_jalan_name))]):
                record.button_draft()
                record.button_cancel()

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

    @api.depends('uang_jalan_line.nominal_uang_jalan', 'biaya_tambahan_standar')
    def _compute_total_uang_jalan_standar(self):
        for record in self:
            uang_jalan_line = record.sudo().uang_jalan_line
            record.total_uang_jalan_standar = sum(uang_jalan_line.mapped('nominal_uang_jalan')) + record.biaya_tambahan_standar

    @api.depends('uang_jalan_nominal_tree.nominal_uang_jalan', 'biaya_tambahan_nominal_saja')
    def _compute_total_nominal_uang_jalan_saja(self):
        for record in self:
            uang_jalan_nominal_tree = record.sudo().uang_jalan_nominal_tree
            record.total_uang_jalan_nominal_saja = sum(
                uang_jalan_nominal_tree.mapped('nominal_uang_jalan')) + record.biaya_tambahan_nominal_saja

    @api.depends('total_uang_jalan_standar', 'total_uang_jalan_nominal_saja')
    def _compute_total(self):
        for record in self:
            record.total = record.total_uang_jalan_standar + record.total_uang_jalan_nominal_saja

    def validate(self):
        self.state = 'validated'

    def unlink(self):
        if any(record.state not in ('to_submit', 'cancel') for record in self):
            raise UserError("Anda tidak dapat menghapus record yang tidak berada dalam status 'Draft' atau 'Cancel'.")

        return super(UangJalan, self).unlink()

class UangJalanLine(models.Model):
    _name = 'uang.jalan.line'
    _description = 'Uang Jalan Line'

    uang_jalan = fields.Many2one('uang.jalan', invisible=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    customer_id = fields.Many2one('res.partner', 'Customer', compute='_compute_muat_and_bongkar')
    tipe_muatan = fields.Many2one('konfigurasi.tipe.muatan', 'Tipe Muatan', required=True)
    order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order', ondelete='restrict', domain="[('state', 'not in', ['sudah_setor'])]")
    muat = fields.Many2one('konfigurasi.lokasi', 'Muat', compute='_compute_muat_and_bongkar')
    bongkar = fields.Many2one('konfigurasi.lokasi', 'Bongkar', compute='_compute_muat_and_bongkar')
    nominal_uang_jalan = fields.Float('Nominal UJ', default=0, digits=(6, 0))
    keterangan = fields.Text('Keterangan')

    @api.depends('order_pengiriman.alamat_muat', 'order_pengiriman.alamat_bongkar')
    def _compute_muat_and_bongkar(self):
        for record in self:
            record.customer_id = record.order_pengiriman.customer
            record.muat = record.order_pengiriman.alamat_muat
            record.bongkar = record.order_pengiriman.alamat_bongkar

    @api.depends('order_pengiriman')
    def _calculate_nominal_uang_jalan(self):
        nominal_uang_jalan = self.env['konfigurasi.uang.jalan'].search([
            ('customer_id', '=', int(self.customer_id.id)),
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

class UangJalanNominalSaja(models.Model):
    _name = 'uang.jalan.nominal.saja'
    _description = 'Uang Jalan Nominal Saja'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    uang_jalan_nominal_saja = fields.Many2one('uang.jalan', invisible=True)

    muat = fields.Many2one('konfigurasi.lokasi', 'Muat')
    bongkar = fields.Many2one('konfigurasi.lokasi', 'Bongkar')
    nominal_uang_jalan = fields.Float('Nominal UJ', default=0, digits=(6, 0))

