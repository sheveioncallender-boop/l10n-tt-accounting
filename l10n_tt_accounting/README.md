# Trinidad & Tobago Accounting Localization (`l10n_tt_accounting`)

Initial Phase 1 module for Odoo Community + Odoo Mates Full Accounting.

## What it adds
- TTD currency setup with `TT$` symbol
- Company statutory fields: BIR Number, VAT Registration Number, VAT Registered
- VAT taxes: 12.5%, Zero Rated, VAT Exempt, Import VAT
- Starter Trinidad & Tobago chart of accounts
- Sales, Purchase, Bank, Cash, and Miscellaneous journals
- Fiscal positions for Local VAT, VAT Exempt, Export/Zero Rated, and Non-VAT businesses
- Simple menu: Accounting > Configuration > Trinidad & Tobago

## Important design note
This module does **not** replace or modify Odoo Mates Accounting. It sits on top of Odoo Community + Odoo Mates and creates Trinidad & Tobago setup data.

## Install
1. Copy `l10n_tt_accounting` into your Odoo custom addons folder.
2. Restart Odoo.
3. Update Apps List.
4. Install **Trinidad & Tobago Accounting Localization**.
5. Go to Accounting > Configuration > Trinidad & Tobago > Accounting Setup.
6. Click **Apply / Refresh TT Setup** if needed.

## Next Phase
After this is tested, build `l10n_tt_payroll` using Odoo Employees, Attendance, Departments, Contracts, and Odoo Mates Accounting journal entries.
