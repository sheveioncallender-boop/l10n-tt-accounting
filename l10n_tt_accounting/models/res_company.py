from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_tt_bir_number = fields.Char(string='BIR Number')
    l10n_tt_vat_number = fields.Char(string='VAT Registration Number')
    l10n_tt_enable_vat = fields.Boolean(string='VAT Registered', default=True)
    l10n_tt_default_vat_rate = fields.Float(string='Default VAT Rate (%)', default=12.5)
