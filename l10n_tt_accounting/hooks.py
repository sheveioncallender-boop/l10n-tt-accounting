<odoo>
    <record id="view_l10n_tt_setup_list" model="ir.ui.view">
        <field name="name">l10n.tt.setup.list</field>
        <field name="model">l10n.tt.setup</field>
        <field name="arch" type="xml">
            <list>
                <field name="company_id"/>
                <field name="currency_id"/>
                <field name="vat_rate"/>
            </list>
        </field>
    </record>

    <record id="view_l10n_tt_setup_form" model="ir.ui.view">
        <field name="name">l10n.tt.setup.form</field>
        <field name="model">l10n.tt.setup</field>
        <field name="arch" type="xml">
            <form string="Trinidad &amp; Tobago Accounting Setup">
                <header>
                    <button name="action_apply_basic_setup" type="object" string="Apply / Refresh TT Setup" class="btn-primary"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>Trinidad &amp; Tobago Accounting Setup</h1>
                    </div>
                    <group>
                        <group string="Company">
                            <field name="company_id"/>
                            <field name="currency_id"/>
                            <field name="vat_rate"/>
                        </group>
                        <group string="Purpose">
                            <field name="setup_notes" nolabel="1"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="What This Creates">
                            <group>
                                <p>TTD currency setup with TT$ symbol.</p>
                                <p>VAT 12.5%, Zero Rated, VAT Exempt, and Import VAT taxes.</p>
                                <p>Starter Trinidad chart of accounts.</p>
                                <p>Sales, Purchase, Bank, Cash, and Miscellaneous journals.</p>
                                <p>Fiscal positions for local VAT, exempt, export, and non-VAT registered businesses.</p>
                            </group>
                        </page>
                        <page string="Compatibility">
                            <group>
                                <p>This module does not replace Odoo Mates Accounting. It only adds Trinidad &amp; Tobago accounting setup data on top of the accounting engine.</p>
                            </group>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_l10n_tt_setup" model="ir.actions.act_window">
        <field name="name">Trinidad &amp; Tobago Accounting Setup</field>
        <field name="res_model">l10n.tt.setup</field>
        <field name="view_mode">list,form</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">Create your Trinidad &amp; Tobago accounting setup.</p>
        </field>
    </record>
</odoo>
