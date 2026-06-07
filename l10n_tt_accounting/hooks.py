from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    """Apply Trinidad setup to existing companies after install.

    Supports both modern Odoo hook env signature and older cr/registry signatures.
    """
    if not hasattr(env, 'cr'):
        cr, registry = env, None
        env = api.Environment(cr, SUPERUSER_ID, {})

    companies = env['res.company'].search([])
    setup_model = env['l10n.tt.setup']
    for company in companies:
        setup = setup_model.search([('company_id', '=', company.id)], limit=1)
        if not setup:
            setup = setup_model.create({'company_id': company.id})
        setup.action_apply_basic_setup()
