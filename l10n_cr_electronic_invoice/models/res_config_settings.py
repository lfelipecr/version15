# -*- coding: utf-8 -*-

from odoo import api,fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_import_bills = fields.Boolean(string=u"Importación facturas electrónicas",
                                         implied_group='account.group_account_manager')
    einvoice_fields_add = fields.Boolean(string=u"Agregar datos comerciales en XML",implied_group='account.group_account_manager')

    invoice_import_ids = fields.Many2one(comodel_name="account.move.import.config",string=u'Configuración para importar facturas.'
    )

    def set_values(self):
        super(AccountConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('module_import_bills', self.module_import_bills)
        self.env['ir.config_parameter'].set_param('einvoice_fields_add', self.einvoice_fields_add)


    @api.model
    def get_values(self):
        res = super(AccountConfigSettings, self).get_values()
        res.update(module_import_bills=self.env['ir.config_parameter'].get_param('module_import_bills'))
        res.update(einvoice_fields_add=self.env['ir.config_parameter'].get_param('einvoice_fields_add'))

        return res

    def open_params_import_ininvoice(self):
        id=None
        config = self.env['account.move.import.config'].sudo().search([('company_id','=',self.env.company.id),('active','=',True)])
        if config:
            id = config.id


        return {
            'type': 'ir.actions.act_window',
            'name': u'Configuración',
            'view_mode': 'form',
            'res_model': 'account.move.import.config',
            'res_id': id,
            'target': 'current',
            'context': {
                'default_company_id': self.env.company.id,
                'form_view_initial_mode': 'edit',
            }
        }


    #Es importante tener configurado el modelo en la captura del mail
