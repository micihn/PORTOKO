from odoo import api, models, fields

class TabunganPTU(models.Model):
    _name = 'tabungan.ptu'
    _description = 'Tabungan PTU'
    _rec_name = 'kode'

    kode = fields.Char(string="Kode")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    tanggal = fields.Datetime(string="Tanggal", default=fields.Datetime.now())
    karyawan = fields.Many2one('hr.employee', string="Karyawan")
    saldo = fields.Float(string="Saldo", compute="compute_saldo_tabungan")
    nominal_ptu = fields.Float(string="Nominal PTU")
    
    class HrEmployee(models.Model):
        _inherit = 'hr.employee'

        @api.model
        def name_search(self, name='', args=None, operator='ilike', limit=100):
            args = args or []
            domain = []
            if name:
                domain = ['|', ('name', operator, name), ('identification_id', operator, name)]
            employees = self.search(domain + args, limit=limit)
            return employees.name_get()

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('identification_id', operator, name)]
        employees = self.search(domain + args, limit=limit)
        return employees.name_get()
    state = fields.Selection([
        ('draft', "Draft"),
        ('paid', "Paid"),
    ], default='draft', string="State")

    @api.depends('karyawan')
    def compute_saldo_tabungan(self):
        for record in self:
            if record.karyawan:
                tabungan_records = self.env['hr.employee.ptu_line'].search([('employee_id', '=', record.karyawan.id)])
                if bool(tabungan_records):
                    for tabungan in tabungan_records:
                        if tabungan:
                            if tabungan.tipe == 'pengeluaran':
                                record.saldo += tabungan.nominal * -1
                            elif tabungan.tipe == 'pemasukan':
                                record.saldo += tabungan.nominal
                        else:
                            record.saldo = 0.0
                else:
                    record.saldo = 0.0
            else:
                record.saldo = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        records = super(TabunganPTU, self).create(vals_list)
        for record in records:
            record.kode = self.env['ir.sequence'].next_by_code('tabungan.ptu.sequence') or 'New'
        return records

    def create_ptu(self):
        self.env['hr.employee.ptu_line'].create({
            'employee_id': self.karyawan.id,
            'tipe': 'pemasukan',
            'nominal': self.nominal_ptu,
            'state': 'diproses',
        })

        account_settings = self.env['konfigurasi.komisi'].search([('company_id', '=', self.env.company.id)])

        journal_entry_tabungan_ptu = self.env['account.move'].sudo().create({
            'company_id': self.company_id.id,
            'move_type': 'entry',
            'date': self.tanggal,
            'ref': str(self.kode) + str(" - " + self.karyawan.name),
            'journal_id': account_settings.journal_kas_1.id,
            'line_ids': [
                (0, 0, {
                    'name': self.kode,
                    'date': self.tanggal,
                    'account_id': account_settings.account_kas_1.id,
                    'company_id': self.company_id.id,
                    'debit': self.nominal_ptu,
                }),

                (0, 0, {
                    'name': self.kode,
                    'date': self.tanggal,
                    'account_id': account_settings.piutang_komisi.id,
                    'company_id': self.company_id.id,
                    'credit': self.nominal_ptu,
                }),
            ],
        })
        journal_entry_tabungan_ptu.action_post()

        self.state = 'paid'
