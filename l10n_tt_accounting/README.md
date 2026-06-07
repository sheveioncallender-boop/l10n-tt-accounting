# Trinidad & Tobago Accounting Localization

## v1.7.0 Trinidad VAT Returns

Adds:

Accounting → Reporting → Trinidad VAT Returns

Each VAT Return tracks:
- Output VAT collected
- Input VAT claimable
- Import VAT placeholder
- Net VAT payable
- VAT payments made
- Balance due / refundable
- Status: Draft, Ready to File, Filed, Paid, Closed

This does not change Odoo's accounting flow. It reads posted journal entries from the VAT accounts and allows users to link cheque/bank/payment journal lines to a VAT period.
