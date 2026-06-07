from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    """Apply Trinidad setup to all companies after install."""
    if not hasattr(env, 'cr'):
        cr = env
        env = api.Environment(cr, SUPERUSER_ID, {})

    setup_model = env['l10n.tt.setup'].sudo()
    for company in env['res.company'].sudo().search([]):
        setup = setup_model.search([('company_id', '=', company.id)], limit=1)
        if not setup:
            setup = setup_model.create({'company_id': company.id})
        setup.action_apply_basic_setup()
