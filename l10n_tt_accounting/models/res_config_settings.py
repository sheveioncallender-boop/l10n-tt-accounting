from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_tt_country_id = fields.Many2one(
        'res.country',
        string='Trinidad & Tobago Country',
        related='company_id.country_id',
        readonly=False,
    )
    l10n_tt_currency_id = fields.Many2one(
        'res.currency',
        string='Trinidad & Tobago Currency',
        related='company_id.currency_id',
        readonly=False,
    )
    l10n_tt_bir_number = fields.Char(
        string='BIR Number',
        related='company_id.l10n_tt_bir_number',
        readonly=False,
    )
    l10n_tt_vat_number = fields.Char(
        string='VAT Registration Number',
        related='company_id.l10n_tt_vat_number',
        readonly=False,
    )
    l10n_tt_enable_vat = fields.Boolean(
        string='VAT Registered',
        related='company_id.l10n_tt_enable_vat',
        readonly=False,
    )
    l10n_tt_default_vat_rate = fields.Float(
        string='Default VAT Rate (%)',
        related='company_id.l10n_tt_default_vat_rate',
        readonly=False,
    )

    def action_l10n_tt_open_setup(self):
        setup = self.env['l10n.tt.setup'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not setup:
            setup = self.env['l10n.tt.setup'].create({'company_id': self.env.company.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trinidad & Tobago Accounting Setup',
            'res_model': 'l10n.tt.setup',
            'res_id': setup.id,
            'view_mode': 'form',
            'target': 'current',
        }
