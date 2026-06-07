from odoo import fields, models, _


class L10nTTSetup(models.Model):
    _name = 'l10n.tt.setup'
    _description = 'Trinidad and Tobago Accounting Setup'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self._default_tt_country())
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=False)
    vat_rate = fields.Float(default=12.5, string='Standard VAT Rate (%)')
    bank_line_ids = fields.One2many('l10n.tt.setup.bank', 'setup_id', string='Bank Accounts')
    bank_account_display_style = fields.Selection([
        ('name_only', 'Bank Name Only'),
        ('last4', 'Bank Name + Last 4 Digits'),
        ('full', 'Bank Name + Full Account Number'),
    ], string='Bank Account Display Style', default='last4',
       help='Controls how bank account numbers appear in chart of account and bank journal names.')
    setup_notes = fields.Text(default='Safe setup assistant for Trinidad & Tobago. It prepares Trinidad-specific accounting options without changing Odoo\'s original accounting flow.')
    apply_company_defaults = fields.Boolean(string='Set Company Country, Fiscal Country & Currency', default=True)
    apply_chart_accounts = fields.Boolean(string='Create Trinidad Chart of Accounts', default=True)
    apply_vat_taxes = fields.Boolean(string='Create Trinidad VAT Taxes', default=True)
    apply_default_taxes = fields.Boolean(string='Set VAT 12.5% as Default Sales/Purchase Tax', default=True)
    apply_journals = fields.Boolean(string='Create Trinidad Journals', default=True)
    apply_bank_accounts = fields.Boolean(string='Create Selected Bank Journals', default=True)
    apply_fiscal_positions = fields.Boolean(string='Create Trinidad Fiscal Positions', default=True)
    apply_accounting_defaults = fields.Boolean(string='Set Safe Accounting Defaults', default=False)

    readiness_status = fields.Selection([
        ('not_checked', 'Not Checked'),
        ('ready', 'Ready'),
        ('needs_attention', 'Needs Attention'),
    ], string='Readiness Status', default='not_checked', readonly=True)
    readiness_summary = fields.Text(string='Trinidad Readiness Audit', readonly=True)

    def _default_tt_country(self):
        return self.env['res.country'].search([('code', '=', 'TT')], limit=1)

    def action_apply_basic_setup(self):
        for setup in self:
            accounts = {}

            # Safe order: company/fiscal country first, then tax groups/taxes.
            if setup.apply_company_defaults:
                setup._setup_country_and_currency()

            setup._setup_company_flags()

            if setup.apply_chart_accounts:
                accounts = setup._setup_accounts()

            taxes = {}
            if setup.apply_vat_taxes:
                if not accounts:
                    accounts = setup._setup_accounts()
                taxes = setup._setup_taxes(accounts)

            if setup.apply_default_taxes and taxes:
                setup._setup_default_taxes(taxes)

            if setup.apply_journals:
                if not accounts:
                    accounts = setup._setup_accounts()
                setup._setup_journals(accounts)

            if setup.apply_bank_accounts:
                if not accounts:
                    accounts = setup._setup_accounts()
                setup._setup_selected_banks(accounts)

            if setup.apply_fiscal_positions and taxes:
                setup._setup_fiscal_positions(taxes)

            if setup.apply_accounting_defaults:
                if not accounts:
                    accounts = setup._setup_accounts()
                setup._setup_accounting_defaults(accounts)

        self.action_run_readiness_audit()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Trinidad & Tobago Setup Applied'),
                'message': _('Selected Trinidad & Tobago configuration options were applied and readiness audit was refreshed.'),
                'sticky': False,
                'type': 'success',
            }
        }

    def action_run_readiness_audit(self):
        for setup in self:
            lines = []
            missing = 0

            def add(label, ok, detail=''):
                nonlocal missing
                symbol = '✓' if ok else '⚠'
                if not ok:
                    missing += 1
                lines.append('%s %s%s' % (symbol, label, (': ' + detail) if detail else ''))

            country = self.env['res.country'].search([('code', '=', 'TT')], limit=1)
            company = setup.company_id
            add('Company country is Trinidad & Tobago', bool(country and company.country_id == country),
                company.country_id.name if company.country_id else 'Not set')

            fiscal_country = False
            for field_name in ('account_fiscal_country_id', 'fiscal_country_id'):
                if field_name in company._fields:
                    fiscal_country = company[field_name]
                    break
            add('Fiscal country is Trinidad & Tobago', bool(country and fiscal_country == country),
                fiscal_country.name if fiscal_country else 'Not set')

            ttd = self.env['res.currency'].with_context(active_test=False).search([('name', '=', 'TTD')], limit=1)
            add('TTD currency exists', bool(ttd))
            add('Company currency is TTD', bool(ttd and company.currency_id == ttd),
                company.currency_id.name if company.currency_id else 'Not set')

            Account = self.env['account.account'].with_company(company)
            def account_exists(code, name):
                domain = [('code', '=', code)]
                if 'company_id' in Account._fields:
                    domain.append(('company_id', '=', company.id))
                elif 'company_ids' in Account._fields:
                    domain.append(('company_ids', 'in', company.id))
                return bool(Account.search(domain, limit=1))

            for code, label in [
                ('130000', 'VAT Input / Recoverable account'),
                ('210000', 'VAT Output / Payable account'),
                ('220000', 'VAT Control account'),
                ('230000', 'PAYE Payable account'),
                ('231000', 'NIS Payable account'),
                ('232000', 'Health Surcharge Payable account'),
            ]:
                add(label, account_exists(code, label), 'missing account code %s' % code)

            Tax = self.env['account.tax'].with_company(company)
            for tax_name, tax_type in [
                ('VAT 12.5% Sales', 'sale'),
                ('VAT 12.5% Purchases', 'purchase'),
                ('Zero Rated Sales 0%', 'sale'),
                ('Zero Rated Purchases 0%', 'purchase'),
                ('VAT Exempt Sales 0%', 'sale'),
                ('VAT Exempt Purchases 0%', 'purchase'),
                ('Import VAT 12.5%', 'purchase'),
            ]:
                add(tax_name, bool(Tax.search([
                    ('name', '=', tax_name),
                    ('company_id', '=', company.id),
                    ('type_tax_use', '=', tax_type)
                ], limit=1)))

            Journal = self.env['account.journal'].with_company(company)
            for code, label in [
                ('TTSJ', 'TT Sales Journal'),
                ('TTPJ', 'TT Purchase Journal'),
                ('TTBK', 'TT Bank Journal'),
                ('TTCS', 'TT Cash Journal'),
                ('TTMJ', 'TT Miscellaneous Journal'),
            ]:
                add(label, bool(Journal.search([('code', '=', code), ('company_id', '=', company.id)], limit=1)))

            FP = self.env['account.fiscal.position'].with_company(company)
            for name in [
                'TT Local VAT Registered',
                'TT VAT Exempt Customer',
                'TT Export / Zero Rated Customer',
                'TT Non-VAT Registered Business',
            ]:
                add(name, bool(FP.search([('name', '=', name), ('company_id', '=', company.id)], limit=1)))

            lines.append('ℹ Bank account display style: %s' % dict(setup._fields['bank_account_display_style'].selection).get(setup.bank_account_display_style, setup.bank_account_display_style))

            if setup.bank_line_ids:
                for line in setup.bank_line_ids:
                    label = 'Bank journal for %s' % line.display_bank_name
                    add(label, bool(line.journal_id), 'not created yet')
            else:
                lines.append('ℹ No bank accounts selected in the Bank Accounts tab.')

            setup.readiness_summary = '\n'.join(lines)
            setup.readiness_status = 'ready' if missing == 0 else 'needs_attention'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Trinidad Readiness Audit Complete'),
                'message': _('Audit completed. Review the Trinidad Readiness Audit section.'),
                'sticky': False,
                'type': 'info',
            }
        }

    def _setup_country_and_currency(self):
        country = self.env['res.country'].search([('code', '=', 'TT')], limit=1)
        if country:
            self.country_id = country.id
            self.company_id.country_id = country.id
            # Odoo versions/accounting modules may use different technical field names.
            for field_name in ('account_fiscal_country_id', 'fiscal_country_id'):
                if field_name in self.company_id._fields:
                    self.company_id[field_name] = country.id

        Currency = self.env['res.currency'].with_context(active_test=False)
        ttd = Currency.search([('name', '=', 'TTD')], limit=1)
        if not ttd:
            ttd = Currency.create({
                'name': 'TTD',
                'symbol': 'TT$',
                'position': 'before',
                'rounding': 0.01,
                'decimal_places': 2,
                'active': True,
            })
        else:
            vals = {'symbol': 'TT$', 'position': 'before', 'active': True}
            if 'decimal_places' in ttd._fields:
                vals['decimal_places'] = 2
            ttd.write(vals)
        self.company_id.currency_id = ttd.id

    def _setup_company_flags(self):
        vals = {}
        if 'l10n_tt_enable_vat' in self.company_id._fields:
            vals['l10n_tt_enable_vat'] = True
        if 'l10n_tt_default_vat_rate' in self.company_id._fields:
            vals['l10n_tt_default_vat_rate'] = self.vat_rate
        if vals:
            self.company_id.write(vals)

    def _create_account(self, code, name, account_type, reconcile=False):
        Account = self.env['account.account'].with_company(self.company_id)
        domain = [('code', '=', code)]
        if 'company_id' in Account._fields:
            domain.append(('company_id', '=', self.company_id.id))
        elif 'company_ids' in Account._fields:
            domain.append(('company_ids', 'in', self.company_id.id))
        account = Account.search(domain, limit=1)
        vals = {'code': code, 'name': name, 'account_type': account_type}
        if 'reconcile' in Account._fields:
            vals['reconcile'] = reconcile
        if not account:
            if 'company_id' in Account._fields:
                vals['company_id'] = self.company_id.id
            elif 'company_ids' in Account._fields:
                vals['company_ids'] = [(4, self.company_id.id)]
            account = Account.create(vals)
        else:
            account.write(vals)
        return account

    def _setup_accounts(self):
        plan = [
            ('100000', 'Cash and Bank', 'asset_cash', False),
            ('101000', 'Cash on Hand', 'asset_cash', False),
            ('102000', 'Bank Account', 'asset_cash', False),
            ('103000', 'Republic Bank Account', 'asset_cash', False),
            ('104000', 'First Citizens Bank Account', 'asset_cash', False),
            ('110000', 'Accounts Receivable', 'asset_receivable', True),
            ('120000', 'Inventory / Stock', 'asset_current', False),
            ('130000', 'VAT Input / Recoverable', 'asset_current', False),
            ('140000', 'Prepayments', 'asset_prepayments', False),
            ('150000', 'Fixed Assets', 'asset_fixed', False),
            ('200000', 'Accounts Payable', 'liability_payable', True),
            ('210000', 'VAT Output / Payable', 'liability_current', False),
            ('220000', 'VAT Control', 'liability_current', False),
            ('230000', 'PAYE Payable', 'liability_current', False),
            ('231000', 'NIS Payable', 'liability_current', False),
            ('232000', 'Health Surcharge Payable', 'liability_current', False),
            ('240000', 'Accrued Expenses', 'liability_current', False),
            ('300000', 'Share Capital / Owner Equity', 'equity', False),
            ('310000', 'Retained Earnings', 'equity_unaffected', False),
            ('400000', 'Product Sales', 'income', False),
            ('401000', 'Service Revenue', 'income', False),
            ('402000', 'Export Sales', 'income', False),
            ('410000', 'Other Income', 'income_other', False),
            ('500000', 'Cost of Goods Sold', 'expense_direct_cost', False),
            ('600000', 'Operating Expenses', 'expense', False),
            ('610000', 'Salaries and Wages', 'expense', False),
            ('611000', 'Employer NIS Expense', 'expense', False),
            ('620000', 'Rent Expense', 'expense', False),
            ('621000', 'Electricity Expense', 'expense', False),
            ('622000', 'Telephone and Internet Expense', 'expense', False),
            ('623000', 'Motor Vehicle Expense', 'expense', False),
            ('624000', 'Bank Charges', 'expense', False),
            ('625000', 'Repairs and Maintenance', 'expense', False),
        ]
        return {code: self._create_account(code, name, typ, rec) for code, name, typ, rec in plan}

    def _tax_group(self, name):
        TaxGroup = self.env['account.tax.group'].with_company(self.company_id)
        country = self.country_id or self.env['res.country'].search([('code', '=', 'TT')], limit=1)
        domain = [('name', '=', name)]
        if 'company_id' in TaxGroup._fields:
            domain.append(('company_id', '=', self.company_id.id))
        if 'country_id' in TaxGroup._fields and country:
            domain.append(('country_id', '=', country.id))
        group = TaxGroup.search(domain, limit=1)

        vals = {'name': name}
        if 'company_id' in TaxGroup._fields:
            vals['company_id'] = self.company_id.id
        if 'country_id' in TaxGroup._fields and country:
            vals['country_id'] = country.id

        if not group:
            group = TaxGroup.create(vals)
        else:
            group.write(vals)
        return group

    def _create_tax(self, name, amount, tax_type, account, description=None):
        Tax = self.env['account.tax'].with_company(self.company_id)
        country = self.country_id or self.env['res.country'].search([('code', '=', 'TT')], limit=1)
        tax_group = self._tax_group('Trinidad & Tobago VAT')

        domain = [('name', '=', name), ('company_id', '=', self.company_id.id), ('type_tax_use', '=', tax_type)]
        if 'country_id' in Tax._fields and country:
            domain.append(('country_id', '=', country.id))
        tax = Tax.search(domain, limit=1)

        vals = {
            'name': name,
            'amount': amount,
            'amount_type': 'percent',
            'type_tax_use': tax_type,
            'company_id': self.company_id.id,
            'tax_group_id': tax_group.id,
            'description': description or name,
        }
        if 'country_id' in Tax._fields and country:
            vals['country_id'] = country.id
        if 'price_include_override' in Tax._fields:
            vals['price_include_override'] = 'tax_excluded'

        if not tax:
            tax = Tax.create(vals)
        else:
            tax.write(vals)

        # Map tax repartition lines to Trinidad VAT control accounts where possible.
        if account:
            for line in tax.invoice_repartition_line_ids | tax.refund_repartition_line_ids:
                if line.repartition_type == 'tax' and 'account_id' in line._fields:
                    line.account_id = account.id
        return tax

    def _setup_taxes(self, accounts):
        vat_output = accounts.get('210000')
        vat_input = accounts.get('130000')
        taxes = {
            'sale_vat': self._create_tax('VAT 12.5% Sales', self.vat_rate, 'sale', vat_output, 'VAT 12.5%'),
            'purchase_vat': self._create_tax('VAT 12.5% Purchases', self.vat_rate, 'purchase', vat_input, 'VAT 12.5%'),
            'sale_zero': self._create_tax('Zero Rated Sales 0%', 0.0, 'sale', None, 'Zero Rated'),
            'purchase_zero': self._create_tax('Zero Rated Purchases 0%', 0.0, 'purchase', None, 'Zero Rated'),
            'sale_exempt': self._create_tax('VAT Exempt Sales 0%', 0.0, 'sale', None, 'VAT Exempt'),
            'purchase_exempt': self._create_tax('VAT Exempt Purchases 0%', 0.0, 'purchase', None, 'VAT Exempt'),
            'import_vat': self._create_tax('Import VAT 12.5%', self.vat_rate, 'purchase', vat_input, 'Import VAT'),
        }
        return taxes

    def _setup_default_taxes(self, taxes):
        vals = {}
        for field_name, tax_key in (
            ('account_sale_tax_id', 'sale_vat'),
            ('account_purchase_tax_id', 'purchase_vat'),
            ('sale_tax_id', 'sale_vat'),
            ('purchase_tax_id', 'purchase_vat'),
        ):
            if field_name in self.company_id._fields and taxes.get(tax_key):
                vals[field_name] = taxes[tax_key].id
        if vals:
            self.company_id.write(vals)

    def _setup_accounting_defaults(self, accounts):
        vals = {}
        default_map = {
            'account_default_pos_receivable_account_id': accounts.get('110000'),
            'account_journal_suspense_account_id': accounts.get('102000'),
            'account_journal_payment_debit_account_id': accounts.get('102000'),
            'account_journal_payment_credit_account_id': accounts.get('102000'),
        }
        for field, account in default_map.items():
            if field in self.company_id._fields and account:
                vals[field] = account.id
        if vals:
            self.company_id.write(vals)

    def _setup_journals(self, accounts):
        Journal = self.env['account.journal'].with_company(self.company_id)
        journals = [
            ('TT Sales Journal', 'sale', 'TTSJ'),
            ('TT Purchase Journal', 'purchase', 'TTPJ'),
            ('TT Bank Journal', 'bank', 'TTBK'),
            ('TT Cash Journal', 'cash', 'TTCS'),
            ('TT Miscellaneous Journal', 'general', 'TTMJ'),
        ]
        for name, jtype, code in journals:
            journal = Journal.search([('code', '=', code), ('company_id', '=', self.company_id.id)], limit=1)
            if not journal:
                vals = {'name': name, 'type': jtype, 'code': code, 'company_id': self.company_id.id}
                if jtype in ('bank', 'cash') and 'default_account_id' in Journal._fields and accounts.get('102000'):
                    vals['default_account_id'] = accounts['102000'].id
                journal = Journal.create(vals)


    def _next_available_account_code(self, base_code):
        Account = self.env['account.account'].with_company(self.company_id)
        code = base_code
        i = 0
        while True:
            domain = [('code', '=', code)]
            if 'company_id' in Account._fields:
                domain.append(('company_id', '=', self.company_id.id))
            elif 'company_ids' in Account._fields:
                domain.append(('company_ids', 'in', self.company_id.id))
            if not Account.search(domain, limit=1):
                return code
            i += 1
            code = str(int(base_code) + i).zfill(len(base_code))

    def _unique_journal_code(self, preferred_code):
        Journal = self.env['account.journal'].with_company(self.company_id)
        code = preferred_code[:5].upper()
        if not Journal.search([('code', '=', code), ('company_id', '=', self.company_id.id)], limit=1):
            return code
        for i in range(1, 100):
            suffix = str(i)
            candidate = (code[:max(1, 5 - len(suffix))] + suffix).upper()
            if not Journal.search([('code', '=', candidate), ('company_id', '=', self.company_id.id)], limit=1):
                return candidate
        return code[:3] + '99'

    def _format_bank_account_name(self, line):
        account_name = line.display_bank_name
        if line.account_type:
            account_name += ' - ' + dict(line._fields['account_type'].selection).get(line.account_type, line.account_type)

        if line.account_number:
            if self.bank_account_display_style == 'full':
                account_name += ' ' + line.account_number
            elif self.bank_account_display_style == 'last4':
                clean = line.account_number.strip()
                account_name += ' ****' + clean[-4:]
            # name_only intentionally hides the account number in the account/journal name.

        return account_name

    def _setup_selected_banks(self, accounts):
        if not self.bank_line_ids:
            return
        Journal = self.env['account.journal'].with_company(self.company_id)
        for line in self.bank_line_ids:
            if not line.account_number:
                continue
            account_name = self._format_bank_account_name(line)

            if not line.account_id:
                account_code = self._next_available_account_code(line.suggested_account_code)
                account = self._create_account(account_code, account_name, 'asset_cash', False)
                line.account_id = account.id
            else:
                account = line.account_id
                account.write({'name': account_name})

            journal_name = account_name
            journal = line.journal_id
            if not journal:
                journal = Journal.search([('name', '=', journal_name), ('company_id', '=', self.company_id.id), ('type', '=', 'bank')], limit=1)
            vals = {
                'name': journal_name,
                'type': 'bank',
                'company_id': self.company_id.id,
            }
            if 'code' in Journal._fields and not journal:
                vals['code'] = self._unique_journal_code(line.suggested_journal_code)
            if 'default_account_id' in Journal._fields:
                vals['default_account_id'] = account.id
            if not journal:
                journal = Journal.create(vals)
            else:
                vals.pop('code', None)
                journal.write(vals)
            line.journal_id = journal.id

            # Store real bank account number on the journal when standard Odoo supports it.
            if 'bank_account_id' in Journal._fields and not journal.bank_account_id:
                PartnerBank = self.env['res.partner.bank'].sudo()
                bank_vals = {
                    'acc_number': line.account_number,
                    'partner_id': self.company_id.partner_id.id,
                    'company_id': self.company_id.id,
                }
                if 'currency_id' in PartnerBank._fields and line.currency_id:
                    bank_vals['currency_id'] = line.currency_id.id
                partner_bank = PartnerBank.search([
                    ('acc_number', '=', line.account_number),
                    ('partner_id', '=', self.company_id.partner_id.id)
                ], limit=1)
                if not partner_bank:
                    partner_bank = PartnerBank.create(bank_vals)
                journal.bank_account_id = partner_bank.id

    def _setup_fiscal_positions(self, taxes):
        FP = self.env['account.fiscal.position'].with_company(self.company_id)
        fiscal_positions = [
            'TT Local VAT Registered',
            'TT VAT Exempt Customer',
            'TT Export / Zero Rated Customer',
            'TT Non-VAT Registered Business',
        ]
        for name in fiscal_positions:
            fp = FP.search([('name', '=', name), ('company_id', '=', self.company_id.id)], limit=1)
            if not fp:
                vals = {'name': name, 'company_id': self.company_id.id}
                if 'auto_apply' in FP._fields:
                    vals['auto_apply'] = False
                fp = FP.create(vals)

            # Odoo versions differ here. Some versions use tax mapping lines,
            # while newer/community/Odoo Mates combinations may expose tax_ids
            # differently. To avoid disrupting standard flow, we only create
            # mappings when the expected mapping line fields exist.
            mapping_field = None
            for candidate in ('tax_ids', 'tax_map_ids'):
                if candidate in fp._fields:
                    mapping_field = candidate
                    break

            if not mapping_field:
                continue

            field = fp._fields[mapping_field]
            comodel = getattr(field, 'comodel_name', '')
            if not comodel:
                continue

            Mapping = self.env[comodel]
            mapping_fields = Mapping._fields

            source_field = None
            dest_field = None

            for candidate in ('tax_src_id', 'src_tax_id', 'tax_source_id'):
                if candidate in mapping_fields:
                    source_field = candidate
                    break

            for candidate in ('tax_dest_id', 'dest_tax_id', 'tax_destination_id'):
                if candidate in mapping_fields:
                    dest_field = candidate
                    break

            # If tax_ids is actually a direct account.tax relation, do not write mappings.
            # This prevents errors such as "Invalid field 'tax_src_id' in 'account.tax'".
            if not source_field or not dest_field:
                continue

            if name in ('TT VAT Exempt Customer', 'TT Export / Zero Rated Customer'):
                sale_vat = taxes.get('sale_vat')
                target = taxes.get('sale_exempt') if name == 'TT VAT Exempt Customer' else taxes.get('sale_zero')
                if sale_vat and target:
                    existing = fp[mapping_field].filtered(lambda l: l[source_field] == sale_vat)
                    if not existing:
                        fp.write({
                            mapping_field: [(0, 0, {
                                source_field: sale_vat.id,
                                dest_field: target.id,
                            })]
                        })

class L10nTTSetupBank(models.Model):
    _name = 'l10n.tt.setup.bank'
    _description = 'Trinidad and Tobago Setup Bank Account'
    _order = 'sequence, id'

    BANK_SELECTION = [
        ('republic', 'Republic Bank Limited'),
        ('first_citizens', 'First Citizens Bank'),
        ('scotiabank', 'Scotiabank Trinidad and Tobago'),
        ('rbc', 'RBC Royal Bank Trinidad and Tobago'),
        ('cibc', 'CIBC Caribbean'),
        ('jmmb', 'JMMB Bank'),
        ('unit_trust', 'Unit Trust Corporation'),
        ('ansa', 'ANSA Bank'),
        ('custom', 'Other / Custom Bank'),
    ]

    ACCOUNT_TYPES = [
        ('chequing', 'Chequing'),
        ('savings', 'Savings'),
        ('business', 'Business Account'),
        ('credit_card', 'Credit Card'),
        ('loan', 'Loan Account'),
        ('other', 'Other'),
    ]

    sequence = fields.Integer(default=10)
    setup_id = fields.Many2one('l10n.tt.setup', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='setup_id.company_id', store=True, readonly=True)
    bank_key = fields.Selection(BANK_SELECTION, string='Bank', required=True, default='republic')
    custom_bank_name = fields.Char(string='Custom Bank Name')
    account_type = fields.Selection(ACCOUNT_TYPES, string='Account Type', required=True, default='chequing')
    account_number = fields.Char(string='Account Number')
    branch_name = fields.Char(string='Branch')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    account_id = fields.Many2one('account.account', string='Chart of Account', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Bank Journal', readonly=True)

    @property
    def display_bank_name(self):
        self.ensure_one()
        if self.bank_key == 'custom' and self.custom_bank_name:
            return self.custom_bank_name
        return dict(self.BANK_SELECTION).get(self.bank_key, 'Bank Account')

    @property
    def suggested_account_code(self):
        self.ensure_one()
        base_map = {
            'republic': '102100',
            'first_citizens': '102200',
            'scotiabank': '102300',
            'rbc': '102400',
            'cibc': '102500',
            'jmmb': '102600',
            'unit_trust': '102700',
            'ansa': '102800',
            'custom': '102900',
        }
        return base_map.get(self.bank_key, '102900')

    @property
    def suggested_journal_code(self):
        self.ensure_one()
        code_map = {
            'republic': 'RBL',
            'first_citizens': 'FCB',
            'scotiabank': 'SCOT',
            'rbc': 'RBC',
            'cibc': 'CIBC',
            'jmmb': 'JMMB',
            'unit_trust': 'UTC',
            'ansa': 'ANSA',
            'custom': 'BANK',
        }
        return code_map.get(self.bank_key, 'BANK')
