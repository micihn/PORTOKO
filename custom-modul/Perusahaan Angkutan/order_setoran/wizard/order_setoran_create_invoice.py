from odoo import models, fields, api
import itertools
from odoo.exceptions import ValidationError


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
                'tanggal_order': record.tanggal_order,
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
            # Mencari konfigurasi komisi
            komisi_settings = self.env['konfigurasi.komisi'].sudo().search([('company_id', '=', setoran.company_id.id)])

            # Membuat journal entry komisi sopir
            if setoran.komisi_sopir > 0:
                journal_entry_komisi_sopir = self.env['account.move'].sudo().create({
                    'company_id': self.env.company.id,
                    'move_type': 'entry',
                    'date': fields.Datetime.now(),
                    'journal_id': komisi_settings.journal_komisi.id,
                    'ref': str(setoran.kode_order_setoran + " - Komisi Sopir"),
                    'line_ids': [
                        (0, 0, {
                            'name': str(setoran.kode_order_setoran + " - Komisi Sopir"),
                            'date': fields.Datetime.now(),
                            'account_id': komisi_settings.hutang_komisi.id,
                            'company_id': self.env.company.id,
                            'credit': setoran.komisi_sopir,
                        }),

                        (0, 0, {
                            'name': str(setoran.kode_order_setoran + " - Komisi Sopir"),
                            'date': fields.Datetime.now(),
                            'account_id': komisi_settings.expense_komisi.id,
                            'company_id': self.env.company.id,
                            'debit': setoran.komisi_sopir,
                        }),
                    ],
                })
                journal_entry_komisi_sopir.action_post()

            # Membuat journal entry komisi kenek
            if setoran.komisi_kenek > 0:
                journal_entry_komisi_kenek = self.env['account.move'].sudo().create({
                    'company_id': self.env.company.id,
                    'move_type': 'entry',
                    'date': fields.Datetime.now(),
                    'journal_id': komisi_settings.journal_komisi.id,
                    'ref': str(setoran.kode_order_setoran + " - Komisi Kenek"),
                    'line_ids': [
                        (0, 0, {
                            'name': str(setoran.kode_order_setoran + " - Komisi Kenek"),
                            'date': fields.Datetime.now(),
                            'account_id': komisi_settings.hutang_komisi.id,
                            'company_id': self.env.company.id,
                            'credit': setoran.komisi_kenek,
                        }),

                        (0, 0, {
                            'name': str(setoran.kode_order_setoran + " - Komisi Kenek"),
                            'date': fields.Datetime.now(),
                            'account_id': komisi_settings.expense_komisi.id,
                            'company_id': self.env.company.id,
                            'debit': setoran.komisi_kenek,
                        }),
                    ],
                })
                journal_entry_komisi_kenek.action_post()

            # Mencari konfigurasi setoran
            account_settings = self.env['konfigurasi.account.setoran'].search([('company_id', '=', setoran.company_id.id)])
            account_kas = account_settings.account_kas
            account_piutang = account_settings.account_piutang
            account_biaya_ujt = account_settings.account_biaya_ujt
            journal_setoran = account_settings.journal_setoran

            if bool(account_kas) == False:
                raise ValidationError("Konfigurasi Account belum diisi! Lakukan konfigurasi di Order Setoran > Konfigurasi")

            if bool(account_piutang) == False:
                raise ValidationError("Konfigurasi Account belum diisi! Lakukan konfigurasi di Order Setoran > Konfigurasi")

            if bool(account_biaya_ujt) == False:
                raise ValidationError("Konfigurasi Account belum diisi! Lakukan konfigurasi di Order Setoran > Konfigurasi")

            if bool(journal_setoran) == False:
                raise ValidationError("Konfigurasi Account belum diisi! Lakukan konfigurasi di Order Setoran > Konfigurasi")

            # Write nomor surat jalan
            for detail in setoran.detail_order:
                detail.order_pengiriman.write({
                    'is_sudah_disetor': True,
                    'state': 'sudah_setor',
                    'nomor_surat_jalan': detail.nomor_surat_jalan or None,
                    'nomor_setoran': setoran.kode_order_setoran or None,
                })

            # Membuat Invoice
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

                invoice = self.env['account.move'].sudo().create({
                    'company_id': self.env.company.id,
                    'move_type': 'out_invoice',
                    'invoice_date': order.tanggal_order,
                    'date': order.tanggal_order,
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

                invoice.action_post()

            # Membuat Vendor Bill (List Pembelian)
            if setoran.total_pembelian > 0:
                for bill in setoran.list_pembelian.order_pengiriman:
                    for purchase in bill.biaya_pembelian:
                        vendor_bill = self.env['account.move'].sudo().create({
                            'company_id': self.env.company.id,
                            'move_type': 'in_invoice',
                            'invoice_date': bill.create_date,
                            'date': bill.create_date,
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
                        vendor_bill.action_post()

            # Membuat Vendor Bill (Biaya Fee)
            if setoran.total_biaya_fee > 0:
                for fee in setoran.biaya_fee:
                    vendor_bill = self.env['account.move'].sudo().create({
                        'company_id': self.env.company.id,
                        'move_type': 'in_invoice',
                        'invoice_date': setoran.tanggal_st,
                        'date': setoran.tanggal_st,
                        'partner_id': fee.fee_contact.id,
                        'currency_id': self.env.user.company_id.currency_id.id,
                        'ref': fee.order_pengiriman.order_pengiriman_name,
                        'nomor_setoran': setoran.kode_order_setoran,
                        'invoice_line_ids': [
                            (0, 0, {
                                'product_id': find_master_pembelian(self),
                                'name': 'Jasa Pengiriman',
                                'price_unit': fee.nominal,
                                'tax_ids': None,
                            })
                        ],
                    })
                    vendor_bill.action_post()

            tanggal_uang_jalan = []
            for rec in setoran.list_uang_jalan:
                tanggal_uang_jalan.append(rec.create_date)

            formatted_dates = [date.strftime('%d/%m/%Y') for date in tanggal_uang_jalan]
            formatted_dates_str = ', '.join(formatted_dates)

            # Buat dan Validate Journal Entry pencatatan pengeluaran
            # Jika 'Total Pengeluaran' > 'Total Uang Jalan', maka hasil pengurangan akan dibuatkan journal
            # entry tambahan
            if setoran.total_pengeluaran > setoran.total_uang_jalan:
                setoran.jenis_pemakaian_uang = 'uang_sendiri'
                # Journal Entry untuk selisih
                journal_entry_selisih = self.env['account.move'].create({
                    'company_id': setoran.company_id.id,
                    'move_type': 'entry',
                    'journal_id': journal_setoran.id,
                    'date': setoran.create_date,
                    'ref': str("Selisih - ") + str(setoran.kode_order_setoran) + str(" - US"),
                    'line_ids': [
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_kas.id,
                            'company_id': setoran.company_id.id,
                            'credit': setoran.total_pengeluaran - setoran.total_uang_jalan,
                        }),
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_piutang.id,
                            'company_id': setoran.company_id.id,
                            'debit': setoran.total_pengeluaran - setoran.total_uang_jalan,
                        }),
                    ],
                })
                journal_entry_selisih.action_post()
                # Journal Entry untuk pemindahan account
                journal_entry_total_pengeluaran = self.env['account.move'].create({
                    'company_id': setoran.company_id.id,
                    'move_type': 'entry',
                    'journal_id': journal_setoran.id,
                    'date': setoran.create_date,
                    'ref': setoran.kode_order_setoran,
                    'line_ids': [
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_biaya_ujt.id,
                            'company_id': setoran.company_id.id,
                            'debit': setoran.total_pengeluaran,
                        }),
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_piutang.id,
                            'company_id': setoran.company_id.id,
                            'credit': setoran.total_pengeluaran,
                        }),
                    ],
                })
                journal_entry_total_pengeluaran.action_post()
            
            # Jika 'Total Uang Jalan' > 'Total Pengeluaran', maka kelebihan dana akan dibuatkan journal
            elif setoran.total_uang_jalan > setoran.total_pengeluaran:
                setoran.jenis_pemakaian_uang = 'kas_lebih'
                # Journal Entry untuk selisih
                journal_entry_selisih = self.env['account.move'].create({
                    'company_id': setoran.company_id.id,
                    'move_type': 'entry',
                    'journal_id': journal_setoran.id,
                    'date': setoran.create_date,
                    'ref': str("Selisih - ") + str(setoran.kode_order_setoran) + str(" - KL"),
                    'line_ids': [
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_kas.id,
                            'company_id': setoran.company_id.id,
                            'debit': setoran.total_uang_jalan - setoran.total_pengeluaran,
                        }),
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_piutang.id,
                            'company_id': setoran.company_id.id,
                            'credit': setoran.total_uang_jalan - setoran.total_pengeluaran,
                        }),
                    ],
                })
                journal_entry_selisih.action_post()
                
                # Journal Entry untuk pemindahan account
                journal_entry_total_pengeluaran = self.env['account.move'].create({
                    'company_id': setoran.company_id.id,
                    'move_type': 'entry',
                    'date': setoran.create_date,
                    'journal_id': journal_setoran.id,
                    'ref': setoran.kode_order_setoran,
                    'line_ids': [
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_biaya_ujt.id,
                            'company_id': setoran.company_id.id,
                            'debit': setoran.total_pengeluaran,
                        }),

                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_piutang.id,
                            'company_id': setoran.company_id.id,
                            'credit': setoran.total_pengeluaran,
                        }),
                    ],
                })
                journal_entry_total_pengeluaran.action_post()

            elif setoran.total_uang_jalan == setoran.total_pengeluaran:
                # Journal Entry untuk pemindahan account
                journal_entry_total_pengeluaran = self.env['account.move'].create({
                    'company_id': setoran.company_id.id,
                    'move_type': 'entry',
                    'date': setoran.create_date,
                    'journal_id': journal_setoran.id,
                    'ref': setoran.kode_order_setoran,
                    'line_ids': [
                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_biaya_ujt.id,
                            'company_id': setoran.company_id.id,
                            'debit': setoran.total_pengeluaran,
                        }),

                        (0, 0, {
                            'name': setoran.kode_order_setoran,
                            'date': setoran.create_date,
                            'account_id': account_piutang.id,
                            'company_id': setoran.company_id.id,
                            'credit': setoran.total_pengeluaran,
                        }),
                    ],
                })
                journal_entry_total_pengeluaran.action_post()

            # This will close uang jalan
            for uj in setoran.list_uang_jalan:
                uj.uang_jalan_name.state = 'closed'
                uj.uang_jalan_name.nomor_setoran = setoran.kode_order_setoran

            # Block dibawah akan mengurangi saldo uang jalan gantung
            for uj in setoran.list_uang_jalan:
                if uj.uang_jalan_name.balance_uang_jalan > 0:
                    # Deakumulasi kas gantung kepada kendaraan
                    setoran.kendaraan.kas_gantung_vehicle -= uj.uang_jalan_name.balance_uang_jalan

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
    tanggal_order = fields.Date('Tanggal Order')
    bayar_dimuka = fields.Float('Bayar Dimuka', digits=(6, 0))
