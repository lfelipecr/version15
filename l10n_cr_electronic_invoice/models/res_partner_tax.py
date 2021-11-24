# -*- coding: utf-8 -*-

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError
import requests
from datetime import datetime, date
from .. import utils

class ResPartnerTax(models.Model):
    _name = "res.partner.tax"
    _description = 'Adicionales para Cliente con exoneración'
    _rec_name = 'numero_documento'

    partner_id = fields.Many2one('res.partner', string='Cliente')
    vat = fields.Char('Identificación')
    numero_documento = fields.Char(string='Número de documento')
    tax_id = fields.Many2one('account.tax', string='Impuesto')
    porcentaje_exoneracion = fields.Float('Porcentaje de exoneración')
    cabys_ids = fields.Many2many('cabys', string='Cabys')
    tipo_documento = fields.Many2one('aut.ex', string='Tipo de documento')
    fecha_emision = fields.Datetime('Fecha emisión')
    fecha_vencimiento = fields.Datetime('Fecha vencimiento')
    institucion = fields.Char(string='Institución')
    date_issue = fields.Date()
    date_expiration = fields.Date()

    #todo hacer un wizard con esto para que me guarde los datos.

    @api.onchange('numero_documento')
    def _onchange_numero_documento(self):
        if self.numero_documento:
            res = utils.customer_exonerated.find_data(self)
            if 'numero_documento' in res:
                self.write(res)
                self._asigned_to_partner()
                res['warning'] = {'title': _('Bien!'), 'message': _('Datos encontrados!')}
                return res

            else:
                return res

    @api.onchange('fecha_emision')
    def _onchange_fecha_emision(self):
        if self.fecha_emision:
            self.date_issue = self.fecha_emision.date()

    @api.onchange('fecha_vencimiento')
    def _onchange_fecha_vencimiento(self):
        if self.fecha_vencimiento:
            self.date_expiration = self.fecha_vencimiento.date()

    @api.model
    def create(self, values):
        res = super(ResPartnerTax, self).create(values)
        self._asigned_to_partner()
        return res

    def write(self, values):
        res = super(ResPartnerTax, self).write(values)
        self._asigned_to_partner()
        return res

    def _asigned_to_partner(self):
        if self.partner_id:
            if not self.partner_id.exoneration_number:
                self.partner_id.exoneration_number = self.id

    @api.depends('numero_documento', 'partner_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.numero_documento
            if record.partner_id:
                name = name + ' / ' + record.partner_id.name
            res.append((record.id, name))
        return res