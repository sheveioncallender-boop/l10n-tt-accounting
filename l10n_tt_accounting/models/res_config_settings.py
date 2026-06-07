from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_tt_country_id = fields.Many2one(
        related='company_id.country_id',
        readonly=False,
        string='Company Country'
    )
    l10n_tt_currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=False,
        string='Company Currency'
    )
    l10n_tt_bir_number = fields.Char(
        related='company_id.l10n_tt_bir_number',
        readonly=False,
        string='BIR Number'
    )
    l10n_tt_vat_number = fields.Char(
        related='company_id.l10n_tt_vat_number',
        readonly=False,
        string='VAT Registration Number'
    )
    l10n_tt_enable_vat = fields.Boolean(
        related='company_id.l10n_tt_enable_vat',
        readonly=False,
        string='VAT Registered'
    )
    l10n_tt_default_vat_rate = fields.Float(
        related='company_id.l10n_tt_default_vat_rate',
        readonly=False,
        string='Default VAT Rate (%)'
    )

    def _get_or_create_l10n_tt_setup(self):
        setup = self.env['l10n.tt.setup'].sudo().search([('company_id', '=', self.env.company.id)], limit=1)
        if not setup:
            setup = self.env['l10n.tt.setup'].sudo().create({'company_id': self.env.company.id})
        return setup

    def action_open_l10n_tt_setup(self):
        setup = self._get_or_create_l10n_tt_setup()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trinidad & Tobago Accounting Setup'),
            'res_model': 'l10n.tt.setup',
            'res_id': setup.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_apply_l10n_tt_setup(self):
        setup = self._get_or_create_l10n_tt_setup()
        return setup.action_apply_basic_setup()
