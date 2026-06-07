# Trinidad & Tobago Accounting Localization

Safe Trinidad & Tobago accounting setup for Odoo Community with Odoo Mates Accounting.

## Key Principle

This module does not replace Odoo Accounting, Odoo Mates Accounting, or Odoo's original accounting flow. It only validates, recommends, and creates missing Trinidad & Tobago components when selected.

## Where to use it

Accounting → Configuration → Trinidad & Tobago → Accounting Setup

## v1.5.0

Added Trinidad Readiness Audit:
- Checks country and fiscal country
- Checks TTD currency
- Checks Trinidad VAT taxes
- Checks key VAT/PAYE/NIS/Health Surcharge accounts
- Checks Trinidad journals
- Checks fiscal positions
- Checks selected bank journals

Use **Run Readiness Audit** first, then **Create Missing / Apply Selected Setup**.
