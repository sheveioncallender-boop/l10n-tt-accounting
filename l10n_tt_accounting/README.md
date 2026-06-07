# Trinidad & Tobago Accounting Localization (`l10n_tt_accounting`)

GitHub-ready Odoo module for **Odoo Community + Odoo Mates Full Accounting**.

## Version 1.2
This version makes the database Trinidad-ready after install:

- Company country: Trinidad & Tobago
- Fiscal country: Trinidad & Tobago where the accounting field exists
- Company currency: TTD
- Currency symbol: `TT$`
- Default Sales VAT: 12.5%
- Default Purchase VAT: 12.5%
- Zero Rated and VAT Exempt taxes
- Import VAT
- Trinidad-oriented chart of accounts
- VAT Input, VAT Output, VAT Control accounts
- PAYE, NIS, and Health Surcharge payable accounts for future payroll
- Sales, Purchase, Bank, Cash, and Miscellaneous journals
- Fiscal positions for Local VAT, VAT Exempt, Export/Zero Rated, and Non-VAT businesses
- Bank setup step for Republic Bank, First Citizens, Scotiabank, RBC, CIBC Caribbean, JMMB, Unit Trust, ANSA Bank, and custom banks
- Automatic bank chart accounts and bank journals from selected bank details

## Important
This does **not** replace Odoo Mates Accounting. It configures Trinidad & Tobago defaults on top of it.

## After update
1. Pull in Cloudpepper.
2. Restart Odoo.
3. Apps > Update Apps List.
4. Upgrade this module.
5. Go to Accounting > Configuration > Trinidad & Tobago > Accounting Setup.
6. Click **Apply / Refresh Trinidad Setup**.
