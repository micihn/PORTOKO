from odoo import models, fields, api
import itertools


class AccountInvoicePayment(models.TransientModel):
    _name = 'account.invoice.payment'
    _description = 'Account Invoice Payment'

    invoice = fields.One2many('account.invoice.payment.line', 'invoice_id', 'Dispatch')

    @api.model
    def default_get(self, active_ids):
        default_vals = super(AccountInvoicePayment, self).default_get(active_ids)

        setoran = self.env['order.setoran'].browse(self._context.get('active_ids', []))

        list_invoice = []
        for record in setoran.detail_order:
            if record.bayar_dimuka == 0:
                pembayaran = 'regular'
            elif record.bayar_dimuka == record.jumlah:
                pembayaran = 'regular'
            elif record.bayar_dimuka < record.jumlah:
                pembayaran = 'dp'
            else:
                pembayaran = False

            list_invoice.append((0,0,{
                'order_pengiriman': record.order_pengiriman.id,
                'customer': record.order_pengiriman.customer.id,
                'pembayaran': pembayaran,
                'nominal_invoice': record.jumlah,
                'bayar_dimuka': record.bayar_dimuka,
                'tanggal_surat_jalan': record.tanggal_surat_jalan,
            }))

        default_vals['invoice'] = list_invoice

        return default_vals

    def create_invoice(self):

        def find_master_pembelian(self):
            # Mengambil ID Database Produk berdasarkan external ID
            external_id = self.env.ref('order_setoran.product_vendor_product_service')
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', int(external_id))]).id
            return product_id

        def find_master_jasa_pengiriman(self):
            # Mengambil ID Database Produk berdasarkan external ID
            external_id = self.env.ref('order_setoran.product_jasa_pengiriman')
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', int(external_id))]).id
            return product_id

        def find_master_down_payment(self):
            # Mengambil ID Database Produk berdasarkan external ID
            external_id = self.env.ref('order_setoran.product_down_payment')
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', int(external_id))]).id
            return product_id

        for setoran in self.env['order.setoran'].browse(self._context.get('active_ids', [])):

            # Write nomor surat jalan
            for detail in setoran.detail_order:
                detail.order_pengiriman.write({
                    'is_sudah_disetor': True,
                    'state': 'sudah_setor',
                    'nomor_surat_jalan': detail.nomor_surat_jalan or None,
                    'tanggal_uang_jalan': detail.tanggal_surat_jalan or None,
                    'nomor_setoran': setoran.kode_order_setoran or None,
                })

            for order in self.invoice:
                if order.pembayaran == 'dp':
                    product_id = find_master_down_payment(self)
                else:
                    product_id = find_master_jasa_pengiriman(self)

                if order.bayar_dimuka == 0:
                    price_unit = order.nominal_invoice
                elif order.bayar_dimuka == order.nominal_invoice:
                    price_unit = order.nominal_invoice
                elif order.bayar_dimuka < order.nominal_invoice:
                    price_unit = order.bayar_dimuka
                else:
                    price_unit = 0

                self.env['account.move'].sudo().create({
                    'company_id': self.env.company.id,
                    'move_type': 'out_invoice',
                    'invoice_date': order.tanggal_surat_jalan,
                    'date': order.tanggal_surat_jalan,
                    'partner_id': order.customer.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'invoice_origin': order.order_pengiriman.order_pengiriman_name,
                    'nomor_setoran': setoran.kode_order_setoran,
                    'invoice_line_ids': [
                        (0, 0, {
                            'product_id' : product_id,
                            'name': 'Jasa Pengiriman',
                            'price_unit': price_unit,
                            'tax_ids': None,
                        })
                    ],
                })

            # Membuat Vendor Bill (List Pembelian)
            if setoran.total_pembelian > 0:
                for bill in setoran.list_pembelian.order_pengiriman:
                    for purchase in bill.biaya_pembelian:
                        self.env['account.move'].sudo().create({
                            'company_id': self.env.company.id,
                            'move_type': 'in_invoice',
                            'invoice_date': bill.tanggal_uang_jalan,
                            'date': bill.tanggal_uang_jalan,
                            'partner_id': purchase.supplier.id,
                            'currency_id': self.env.user.company_id.currency_id.id,
                            'ref': bill.order_pengiriman_name,
                            'nomor_setoran': setoran.kode_order_setoran,
                            'invoice_line_ids': [
                                (0, 0, {
                                    'product_id': find_master_pembelian(self),
                                    'name': 'Jasa Pengiriman',
                                    'price_unit': purchase.nominal,
                                    'tax_ids': None,
                                })
                            ],
                        })

            tanggal_uang_jalan = []
            for rec in setoran.list_uang_jalan:
                tanggal_uang_jalan.append(rec.tanggal)

            formatted_dates = [date.strftime('%d/%m/%Y') for date in tanggal_uang_jalan]
            formatted_dates_str = ', '.join(formatted_dates)

            # Buat Komisi Sopir
            if setoran.komisi_sopir > 0 and setoran.sisa > 0:
                self.env['hr.expense'].sudo().create({
                    'company_id': self.env.company.id,
                    'name': f"Komisi Sopir {setoran.sopir.name} {formatted_dates_str}",
                    'employee_id': setoran.sopir.id,
                    'product_id': find_master_jasa_pengiriman(setoran),
                    'quantity': 1,
                    'total_amount': setoran.komisi_sopir,
                    'payment_mode': 'company_account',
                    'tax_ids': None,
                    'reference': setoran.kode_order_setoran,
                })

            # Buat Komisi Kenek
            if setoran.komisi_kenek > 0 and setoran.sisa > 0:
                self.env['hr.expense'].sudo().create({
                    'company_id': self.env.company.id,
                    'name': f"Komisi Kenek {setoran.kenek.name} {formatted_dates_str}",
                    'employee_id': setoran.kenek.id,
                    'product_id': find_master_jasa_pengiriman(setoran),
                    'quantity': 1,
                    'total_amount': setoran.komisi_kenek,
                    'payment_mode': 'company_account',
                    'tax_ids': None,
                    'reference': setoran.kode_order_setoran,
                })

            setoran.state = 'done'

class AccountInvoicePaymentLine(models.TransientModel):
    _name = "account.invoice.payment.line"

    invoice_id = fields.Many2one('account.invoice.payment', string="Wizard")
    order_pengiriman = fields.Many2one('order.pengiriman', 'No. Order')
    customer = fields.Many2one('res.partner', 'Customer')
    pembayaran = fields.Selection([
        ('regular', 'Regular Payment'),
        ('dp', 'DP (Down Payment)'),
    ], required=True)
    nominal_invoice = fields.Float('Total Tagihan', digits=(6, 0))
    tanggal_surat_jalan = fields.Date('Tanggal Surat Jalan')
    bayar_dimuka = fields.Float('Bayar Dimuka', digits=(6, 0))
