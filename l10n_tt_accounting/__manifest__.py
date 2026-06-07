{
    'name': 'Trinidad & Tobago Accounting Localization',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Trinidad & Tobago accounting setup for Odoo Community with Odoo Mates Accounting',
    'description': '''
Trinidad & Tobago Accounting Localization
=========================================

This module provides a clean Trinidad & Tobago accounting setup layer:
- TTD currency formatting
- VAT 12.5%, VAT Exempt, Zero Rated, and Import VAT taxes
- Trinidad-oriented chart of accounts starter setup
- Sales, Purchase, Bank, and Cash journals
- Fiscal positions for local VAT, VAT exempt, and export/zero-rated customers
- Setup menu and company configuration screen

Designed to sit on top of Odoo Community + Odoo Mates Full Accounting without modifying their accounting engine.
''',
    'author': 'Sheveion Callender / Spxcorp Limited',
    'website': 'https://spxcorp.com',
    'license': 'LGPL-3',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/l10n_tt_setup_views.xml',
        'views/l10n_tt_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
