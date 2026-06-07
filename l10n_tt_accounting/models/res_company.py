from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_tt_bir_number = fields.Char(string='BIR Number')
    l10n_tt_vat_number = fields.Char(string='VAT Registration Number')
    l10n_tt_enable_vat = fields.Boolean(string='VAT Registered', default=True)
    l10n_tt_default_vat_rate = fields.Float(string='Default VAT Rate (%)', default=12.5)
    l10n_tt_company_registration_number = fields.Char(string='Company Registration Number')
    l10n_tt_paye_registration_number = fields.Char(string='PAYE Registration Number')
    l10n_tt_nis_employer_number = fields.Char(string='NIS Employer Number')
    l10n_tt_business_activity = fields.Char(string='Business Activity')
