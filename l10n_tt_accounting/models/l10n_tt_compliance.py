from odoo import fields, models, api, _


class L10nTTCompliance(models.Model):
    _name = 'l10n.tt.compliance'
    _description = 'Trinidad and Tobago Company Compliance'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade',
    )
    company_registration_number = fields.Char(string='Company Registration Number')
    business_activity = fields.Char(string='Business Activity')
    bir_number = fields.Char(string='BIR Number')
    vat_registration_number = fields.Char(string='VAT Registration Number')
    vat_registered = fields.Boolean(string='VAT Registered', default=True)
    paye_registration_number = fields.Char(string='PAYE Registration Number')
    nis_employer_number = fields.Char(string='NIS Employer Number')
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('company_unique', 'unique(company_id)', 'Only one Trinidad compliance profile is allowed per company.'),
    ]

    def action_open_accounting_setup(self):
        self.ensure_one()
        setup = self.env['l10n.tt.setup'].search([('company_id', '=', self.company_id.id)], limit=1)
        if not setup:
            setup = self.env['l10n.tt.setup'].create({'company_id': self.company_id.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trinidad & Tobago Accounting Setup',
            'res_model': 'l10n.tt.setup',
            'res_id': setup.id,
            'view_mode': 'form',
            'target': 'current',
        }
