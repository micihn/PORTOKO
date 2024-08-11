from odoo import api, models, fields
from odoo.exceptions import ValidationError

class PenjualanPTU(models.Model):
    _name = 'penjualan.ptu'
    _description = 'Penjualan PTU'
    _rec_name = 'name'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    name = fields.Char(string='Name', readonly=True, default='New', copy=False)
    date = fields.Datetime(string="Tanggal", default=fields.Datetime.now(), readonly=True)
    karyawan = fields.Many2one('hr.employee', string="Karyawan", states={
		'draft': [('readonly', False)],
		'paid': [('readonly', True)]
	})

    keterangan = fields.Text(string="Keterangan", states={
		'draft': [('readonly', False)],
		'paid': [('readonly', True)]
	})

    penjualan_ptu = fields.One2many('penjualan.ptu.line', 'penjualan_ptu', states={
		'draft': [('readonly', False)],
		'paid': [('readonly', True)]
	})

    ptu_line_id = fields.Integer()

    journal_penjualan_ptu = fields.Integer()

    stock_location = fields.Many2one('stock.location', string="Stock Location", states={
		'draft': [('readonly', False)],
		'paid': [('readonly', True)]
	})

    state = fields.Selection([
        ('draft', "Draft"),
        ('paid', "Paid"),
    ], default='draft', string="State", tracking=True)

    total_penjualan = fields.Float(string="Total Penjualan", compute="compute_total_penjualan")

    @api.depends('penjualan_ptu.subtotal')
    def compute_total_penjualan(self):
        self.total_penjualan = 0

        for line in self.penjualan_ptu:
            self.total_penjualan += line.subtotal

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('penjualan.ptu.sequence') or 'New'
        return super(PenjualanPTU, self).create(vals_list)

    def validate(self):
        for rec in self:
            account_settings = self.env['konfigurasi.penjualan.ptu'].search([('company_id', '=', self.env.company.id)])
            journal_sparepart = account_settings.journal_sparepart.id
            account_piutang_komisi = account_settings.account_piutang_komisi.id
            account_persediaan_sparepart = account_settings.account_persediaan_sparepart.id

            if not rec.stock_location:
                raise ValidationError('Lokasi Stock tidak boleh kosong')

            if not journal_sparepart or not account_piutang_komisi or not account_persediaan_sparepart:
                raise ValidationError("Anda belum melakukan konfigurasi account pada menu Penjualan PTU > Konfigurasi.")

            if rec.total_penjualan > 0:
                create_ptu = self.env['hr.employee.ptu_line'].create({
                    'employee_id': rec.karyawan.id,
                    'tipe': 'pengeluaran',
                    'nominal': rec.total_penjualan,
                    'state': 'diproses',
                })

                rec.ptu_line_id = create_ptu.id

                for line in self.penjualan_ptu:
                    new_stock_move = self.env['stock.move'].create({
                        'name': rec.name,
                        'location_id': rec.stock_location.id,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                        'product_id': line.barang.id,
                        'product_uom_qty': line.qty,
                        'product_uom': line.satuan.id,
                    })

                    new_stock_move._action_confirm()
                    new_stock_move._action_assign()

                    for product in self.env['stock.move'].search([('reference', '=', str(rec.name)), ('state', '=', 'assigned')]):
                        product.move_line_ids.write({'qty_done': line.qty})
                        product._action_done()

                journal_penjualan_ptu = self.env['account.move'].sudo().create({
                    'company_id': self.env.company.id,
                    'move_type': 'entry',
                    'date': rec.date,
                    'journal_id': journal_sparepart,
                    'ref': str(rec.name) + str(" - Penjualan PTU " + rec.karyawan.name),
                    'line_ids': [
                        (0, 0, {
                            'name': rec.name,
                            'date': rec.date,
                            'account_id': account_piutang_komisi,
                            'company_id': self.env.company,
                            'debit': rec.total_penjualan,
                        }),

                        (0, 0, {
                            'name': rec.name,
                            'date': rec.date,
                            'account_id': account_persediaan_sparepart,
                            'company_id': self.env.company,
                            'credit': rec.total_penjualan,
                        }),
                    ],
                })
                journal_penjualan_ptu.action_post()

                rec.journal_penjualan_ptu = journal_penjualan_ptu.id

            else:
                raise ValidationError("Tidak dapat memvalidasi penjualan PTU dengan total 0 rupiah")

        self.state = 'paid'

    def cancel(self):
        for record in self:
            ptu_record = self.env['hr.employee.ptu_line'].sudo().search([('id','=',record.ptu_line_id)])
            for rec_ptu in ptu_record:
                rec_ptu.unlink()

            account_move = self.env['account.move'].search([('id', '=', record.journal_penjualan_ptu)])
            account_move.button_draft()
            account_move.button_cancel()

            for line in self.penjualan_ptu:
                new_stock_move = self.env['stock.move'].create({
                    'name': record.name + str(' - Penjualan PTU Cancelled'),
                    'location_id': self.env.ref('stock.stock_location_customers').id,
                    'location_dest_id': record.stock_location.id,
                    'product_id': line.barang.id,
                    'product_uom_qty': line.qty,
                    'product_uom': line.satuan.id,
                })

                new_stock_move._action_confirm()
                new_stock_move._action_assign()

                for product in self.env['stock.move'].search([('reference', '=', str(record.name)), ('state', '=', 'assigned')]):
                    product.move_line_ids.write({'qty_done': line.qty})
                    product._action_done()

        self.state = 'draft'

class PenjualanPTULine(models.Model):
    _name = 'penjualan.ptu.line'
    _description = 'Penjualan PTU Line'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    penjualan_ptu = fields.Many2one('penjualan.ptu', invisible=True)
    barang = fields.Many2one('product.product',string="Barang")
    qty = fields.Float(string="Qty")
    satuan = fields.Many2one('uom.uom', string="Satuan")
    harga = fields.Float(string="Harga")
    subtotal = fields.Float(string="Jumlah", compute="compute_subtotal")

    @api.onchange('barang')
    def set_uom(self):
        for line in self:
            line.satuan = line.barang.product_tmpl_id.uom_id.id

    @api.onchange('barang')
    def set_saleprice(self):
        for line in self:
            line.harga = line.barang.product_tmpl_id.list_price

    @api.depends('qty', 'harga')
    def compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.harga