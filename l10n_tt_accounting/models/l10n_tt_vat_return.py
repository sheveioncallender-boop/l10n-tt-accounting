from odoo import api, fields, models, _


class L10nTTVATReturn(models.Model):
    _name = 'l10n.tt.vat.return'
    _description = 'Trinidad and Tobago VAT Return'
    _order = 'date_from desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Reference', required=True, default=lambda self: _('New VAT Return'))
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready to File'),
        ('filed', 'Filed'),
        ('paid', 'Paid'),
        ('closed', 'Closed'),
    ], default='draft', string='Status', tracking=True)

    output_vat_account_id = fields.Many2one('account.account', string='Output VAT Account')
    input_vat_account_id = fields.Many2one('account.account', string='Input VAT Account')
    vat_control_account_id = fields.Many2one('account.account', string='VAT Control / Payable Account')
    bir_partner_id = fields.Many2one('res.partner', string='BIR / Tax Authority Partner')

    output_vat_amount = fields.Monetary(string='Output VAT Collected', compute='_compute_vat_amounts', store=True)
    input_vat_amount = fields.Monetary(string='Input VAT Claimable', compute='_compute_vat_amounts', store=True)
    import_vat_amount = fields.Monetary(string='Import VAT', compute='_compute_vat_amounts', store=True)
    net_vat_payable = fields.Monetary(string='Net VAT Payable', compute='_compute_vat_amounts', store=True)
    payments_made = fields.Monetary(string='VAT Payments Made', compute='_compute_vat_amounts', store=True)
    balance_due = fields.Monetary(string='Balance Due / Refundable', compute='_compute_vat_amounts', store=True)
    currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)

    payment_move_line_ids = fields.Many2many(
        'account.move.line',
        'l10n_tt_vat_return_payment_line_rel',
        'vat_return_id',
        'line_id',
        string='Linked VAT Payment Lines',
        help='Optional: manually link bank/payment journal lines related to this VAT return.',
    )
    note = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name') in (False, _('New VAT Return')):
                vals['name'] = self.env['ir.sequence'].next_by_code('l10n.tt.vat.return') or _('New VAT Return')
        return super().create(vals_list)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for rec in self:
            rec._set_default_accounts()

    def _set_default_accounts(self):
        Account = self.env['account.account'].with_company(self.company_id)
        def find(code):
            domain = [('code', '=', code)]
            if 'company_id' in Account._fields:
                domain.append(('company_id', '=', self.company_id.id))
            elif 'company_ids' in Account._fields:
                domain.append(('company_ids', 'in', self.company_id.id))
            return Account.search(domain, limit=1)

        if not self.output_vat_account_id:
            self.output_vat_account_id = find('210000')
        if not self.input_vat_account_id:
            self.input_vat_account_id = find('130000')
        if not self.vat_control_account_id:
            self.vat_control_account_id = find('220000') or find('210000')

        if not self.bir_partner_id:
            partner = self.env['res.partner'].search([('name', '=', 'Board of Inland Revenue')], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': 'Board of Inland Revenue',
                    'company_type': 'company',
                })
            self.bir_partner_id = partner.id

    def action_refresh_amounts(self):
        for rec in self:
            rec._set_default_accounts()
            rec._compute_vat_amounts()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('VAT Return Refreshed'),
                'message': _('VAT figures were recalculated from posted accounting entries.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _sum_account_balance(self, account):
        if not account or not self.date_from or not self.date_to:
            return 0.0
        domain = [
            ('company_id', '=', self.company_id.id),
            ('account_id', '=', account.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', '=', 'posted'),
        ]
        lines = self.env['account.move.line'].search(domain)
        return sum(lines.mapped('balance'))

    def _sum_linked_payments(self):
        self.ensure_one()
        if self.payment_move_line_ids:
            return abs(sum(self.payment_move_line_ids.filtered(lambda l: l.move_id.state == 'posted').mapped('balance')))

        if not self.vat_control_account_id or not self.date_from or not self.date_to:
            return 0.0

        # Safe automatic detection: posted lines on the VAT control/payable account
        # with a partner matching BIR / Tax Authority, during the period.
        domain = [
            ('company_id', '=', self.company_id.id),
            ('account_id', '=', self.vat_control_account_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', '=', 'posted'),
        ]
        if self.bir_partner_id:
            domain.append(('partner_id', '=', self.bir_partner_id.id))
        lines = self.env['account.move.line'].search(domain)
        return abs(sum(lines.mapped('balance')))

    @api.depends(
        'date_from', 'date_to', 'company_id',
        'output_vat_account_id', 'input_vat_account_id', 'vat_control_account_id',
        'payment_move_line_ids.balance', 'payment_move_line_ids.move_id.state',
        'bir_partner_id',
    )
    def _compute_vat_amounts(self):
        for rec in self:
            output_balance = rec._sum_account_balance(rec.output_vat_account_id)
            input_balance = rec._sum_account_balance(rec.input_vat_account_id)

            # In Odoo, output VAT liability is usually a credit balance (negative balance).
            rec.output_vat_amount = abs(output_balance) if output_balance else 0.0

            # Input VAT asset is usually a debit balance (positive balance).
            rec.input_vat_amount = abs(input_balance) if input_balance else 0.0

            rec.import_vat_amount = 0.0
            rec.net_vat_payable = rec.output_vat_amount - rec.input_vat_amount - rec.import_vat_amount
            rec.payments_made = rec._sum_linked_payments()
            rec.balance_due = rec.net_vat_payable - rec.payments_made

    def action_mark_ready(self):
        self.write({'state': 'ready'})

    def action_mark_filed(self):
        self.write({'state': 'filed'})

    def action_mark_paid(self):
        self.write({'state': 'paid'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
