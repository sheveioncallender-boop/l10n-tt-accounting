{
    'name': 'Trinidad & Tobago Accounting Localization',
    'version': '19.0.1.7.0',
    'category': 'Accounting/Localizations',
    'summary': 'Trinidad & Tobago ready accounting setup for Odoo Community with Odoo Mates Accounting',
    'description': '''
Trinidad & Tobago Accounting Localization
=========================================

This module safely prepares Odoo Community + Odoo Mates Accounting for Trinidad & Tobago:
- Optionally sets company country and fiscal country to Trinidad & Tobago
- Sets TTD as company currency with TT$ symbol
- Creates Trinidad-oriented chart of accounts
- Creates VAT 12.5%, Zero Rated, VAT Exempt, and Import VAT taxes
- Optionally sets 12.5% VAT as default sales and purchase tax
- Creates standard sales, purchase, bank, cash, and miscellaneous journals
- Creates fiscal positions for local VAT, exempt, export, and non-VAT customers
- Adds Trinidad company statutory fields for BIR and VAT registration

This module does not replace Odoo Mates Accounting or Odoo's accounting flow. It safely configures Trinidad & Tobago defaults on top of the accounting engine.
''',
    'author': 'Sheveion Callender / Spxcorp Limited',
    'website': 'https://spxcorp.com',
    'license': 'LGPL-3',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_tt_sequences.xml',
        'views/res_company_views.xml',
        'views/l10n_tt_setup_views.xml',
        'views/l10n_tt_compliance_views.xml',
        'views/l10n_tt_vat_return_views.xml',
        'views/l10n_tt_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
