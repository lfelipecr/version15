# -*- coding: utf-8 -*-
from functools import partial

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError
import requests
from datetime import datetime, date

from .. import utils

class PartnerElectronic(models.Model):
    _inherit = "res.partner"

    commercial_name = fields.Char()
    identification_id = fields.Many2one(
        comodel_name="identification.type",
        string="ID Type",
    )
    payment_methods_id = fields.Many2one(
        comodel_name="payment.methods",
    )
    has_exoneration = fields.Boolean()

    exoneration_number = fields.Many2one('res.partner.tax', 'Exoneración')
    institution_name = fields.Char(string="Issuing Institution",related='exoneration_number.institucion')
    date_issue = fields.Date(related='exoneration_number.date_issue')
    date_expiration = fields.Date(related='exoneration_number.date_expiration')
    type_exoneration = fields.Many2one(comodel_name="aut.ex",related='exoneration_number.tipo_documento')
    # tax_id = fields.Many2one('account.tax',string='Impuesto',domain=[('has_exoneration','=',True)])
    # is_expired = fields.Boolean()

    vat = fields.Char(string=u'N°Documento', help="Número de identificación")


    _sql_constraints = [
        (
            "vat_unique",
            "Check(1=1)",
            _("No pueden existir dos clientes/proveedores con el mismo número de identificación"),
        )
    ]

    @api.constrains('vat')
    def _check_unique_vat(self):
        for partner in self:
            if partner.vat:
                p_find = self.sudo().search([('vat','=',partner.vat),('parent_id','=',False),('vat','=',False)])
                if p_find and not partner.parent_id and p_find != partner:
                    raise ValidationError(_(u'No pueden existir dos clientes/proveedores con el mismo número de identificación'))

    # @api.onchange('exoneration_number')
    # def _onchange_exoneration_number(self):
    #
    #     if self.exoneration_number:
    #         res = utils.customer_exonerated.find_data(self)
    #         # is_expired = self.func_expiration(date_due)
    #         if 'numero_documento' in res:
    #             self.update({
    #                 'type_exoneration': res['tipo_documento'],
    #                 'institution_name': res['institucion'],
    #                 'date_issue': datetime.strptime(res['fecha_emision'][0:10], '%Y-%m-%d').date(),
    #                 'date_expiration': datetime.strptime(res['fecha_vencimiento'][0:10], '%Y-%m-%d').date(),
    #             })
    #             res['warning'] = {'title': _('Bien!'), 'message': _('Datos encontrados!')}
    #             return res
    #         else:
    #             return res



    def open_partner_exonerated(self):
        id = None
        partner_tax = self.env['res.partner.tax'].sudo().search(['|', ('partner_id', '=', self.id), ('vat', '=', self.vat)])
        if partner_tax:
            id = partner_tax.id
        view = {
            'type': 'ir.actions.act_window',
            'name': u'Cliente exonerado',
            'view_mode': 'form',
            'res_model': 'res.partner.tax',
            'res_id': id,
            'target': 'current',
            'context': {
                'default_partner_id': self.id,
                'default_vat': self.vat,
                'form_view_initial_mode': 'edit',
            }
        }

        return view
