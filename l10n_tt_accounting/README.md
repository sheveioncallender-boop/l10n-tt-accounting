# Trinidad & Tobago Accounting Localization

Safe Trinidad & Tobago accounting setup for Odoo Community with Odoo Mates Accounting.

## v1.6.0 Safe Compliance

Added a separate Trinidad & Tobago Compliance Profile model:

Accounting → Configuration → Trinidad & Tobago → Compliance Profile

Fields:
- Company Registration Number
- Business Activity
- BIR Number
- VAT Registration Number
- PAYE Registration Number
- NIS Employer Number

Important:
This version does **not** add new compliance columns directly to `res.company`.
This keeps the website, company records, and Odoo core flow safer.

## Existing Features

- Trinidad setup menu under Accounting
- Readiness audit
- Safe setup options
- Bank account display style
- VAT and statutory account checks
