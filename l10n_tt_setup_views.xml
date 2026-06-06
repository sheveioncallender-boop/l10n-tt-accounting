from odoo import api, fields, models, _


class L10nTTSetup(models.Model):
    _name = 'l10n.tt.setup'
    _description = 'Trinidad and Tobago Accounting Setup'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=False)
    vat_rate = fields.Float(default=12.5, string='Standard VAT Rate (%)')
    setup_notes = fields.Text(default='Use this setup as the Trinidad & Tobago localization layer on top of Odoo Community and Odoo Mates Accounting.')

    def action_apply_basic_setup(self):
        for setup in self:
            setup._setup_currency()
            setup._setup_accounts()
            setup._setup_taxes()
            setup._setup_journals()
            setup._setup_fiscal_positions()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Trinidad & Tobago Setup Applied'),
                'message': _('Currency, starter accounts, VAT taxes, journals, and fiscal positions were checked/created.'),
                'sticky': False,
                'type': 'success',
            }
        }

    def _setup_currency(self):
        ttd = self.env['res.currency'].with_context(active_test=False).search([('name', '=', 'TTD')], limit=1)
        if not ttd:
            ttd = self.env['res.currency'].create({
                'name': 'TTD',
                'symbol': 'TT$',
                'position': 'before',
                'rounding': 0.01,
                'decimal_places': 2,
                'active': True,
            })
        else:
            ttd.write({'symbol': 'TT$', 'position': 'before', 'active': True})
        self.company_id.currency_id = ttd.id

    def _account_type(self, code):
        # Odoo 16+ account_type values. Kept simple for Odoo 18/19 Community + accounting modules.
        return code

    def _create_account(self, code, name, account_type):
        Account = self.env['account.account'].with_company(self.company_id)
        account = Account.search([('code', '=', code), ('company_ids', 'in', self.company_id.id)], limit=1)
        vals = {
            'code': code,
            'name': name,
            'account_type': account_type,
        }
        if not account:
            vals['company_ids'] = [(4, self.company_id.id)]
            account = Account.create(vals)
        return account

    def _setup_accounts(self):
        accounts = [
            ('100000', 'Cash and Bank', 'asset_cash'),
            ('101000', 'Cash on Hand', 'asset_cash'),
            ('102000', 'Bank Account', 'asset_cash'),
            ('110000', 'Accounts Receivable', 'asset_receivable'),
            ('120000', 'Inventory', 'asset_current'),
            ('130000', 'VAT Input / Recoverable', 'asset_current'),
            ('200000', 'Accounts Payable', 'liability_payable'),
            ('210000', 'VAT Output / Payable', 'liability_current'),
            ('220000', 'VAT Control', 'liability_current'),
            ('300000', 'Owner Equity / Share Capital', 'equity'),
            ('400000', 'Sales Revenue', 'income'),
            ('401000', 'Export Sales', 'income'),
            ('500000', 'Cost of Goods Sold', 'expense_direct_cost'),
            ('600000', 'Operating Expenses', 'expense'),
            ('610000', 'Payroll Expenses', 'expense'),
        ]
        for code, name, account_type in accounts:
            self._create_account(code, name, account_type)

    def _tax_group(self, name):
        TaxGroup = self.env['account.tax.group'].with_company(self.company_id)
        group = TaxGroup.search([('name', '=', name), ('company_id', '=', self.company_id.id)], limit=1)
        if not group:
            group = TaxGroup.create({'name': name, 'company_id': self.company_id.id})
        return group

    def _create_tax(self, name, amount, tax_type, invoice_account_code=None, refund_account_code=None, description=None):
        Tax = self.env['account.tax'].with_company(self.company_id)
        tax = Tax.search([('name', '=', name), ('company_id', '=', self.company_id.id), ('type_tax_use', '=', tax_type)], limit=1)
        group = self._tax_group('Trinidad & Tobago VAT')
        vals = {
            'name': name,
            'amount': amount,
            'amount_type': 'percent',
            'type_tax_use': tax_type,
            'company_id': self.company_id.id,
            'tax_group_id': group.id,
            'description': description or name,
        }
        if not tax:
            tax = Tax.create(vals)
        else:
            tax.write(vals)
        return tax

    def _setup_taxes(self):
        self._create_tax('VAT 12.5% Sales', self.vat_rate, 'sale', description='VAT 12.5%')
        self._create_tax('VAT 12.5% Purchases', self.vat_rate, 'purchase', description='VAT 12.5%')
        self._create_tax('Zero Rated Sales 0%', 0.0, 'sale', description='Zero Rated')
        self._create_tax('Zero Rated Purchases 0%', 0.0, 'purchase', description='Zero Rated')
        self._create_tax('VAT Exempt Sales 0%', 0.0, 'sale', description='VAT Exempt')
        self._create_tax('VAT Exempt Purchases 0%', 0.0, 'purchase', description='VAT Exempt')
        self._create_tax('Import VAT 12.5%', self.vat_rate, 'purchase', description='Import VAT')

    def _setup_journals(self):
        Journal = self.env['account.journal'].with_company(self.company_id)
        journals = [
            ('TT Sales Journal', 'sale', 'TTSJ'),
            ('TT Purchase Journal', 'purchase', 'TTPJ'),
            ('TT Bank Journal', 'bank', 'TTBK'),
            ('TT Cash Journal', 'cash', 'TTCS'),
            ('TT Miscellaneous Journal', 'general', 'TTMJ'),
        ]
        for name, jtype, code in journals:
            if not Journal.search([('code', '=', code), ('company_id', '=', self.company_id.id)], limit=1):
                Journal.create({'name': name, 'type': jtype, 'code': code, 'company_id': self.company_id.id})

    def _setup_fiscal_positions(self):
        FP = self.env['account.fiscal.position'].with_company(self.company_id)
        for name in ['TT Local VAT Registered', 'TT VAT Exempt Customer', 'TT Export / Zero Rated Customer', 'TT Non-VAT Registered Business']:
            if not FP.search([('name', '=', name), ('company_id', '=', self.company_id.id)], limit=1):
                FP.create({'name': name, 'company_id': self.company_id.id})
