from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Kept for backward compatibility with earlier Settings views.
    l10n_tt_country_id = fields.Many2one('res.country', related='company_id.country_id', readonly=False)
    l10n_tt_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=False)
    l10n_tt_bir_number = fields.Char(related='company_id.l10n_tt_bir_number', readonly=False)
    l10n_tt_vat_number = fields.Char(related='company_id.l10n_tt_vat_number', readonly=False)
    l10n_tt_enable_vat = fields.Boolean(related='company_id.l10n_tt_enable_vat', readonly=False)
    l10n_tt_default_vat_rate = fields.Float(related='company_id.l10n_tt_default_vat_rate', readonly=False)

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
