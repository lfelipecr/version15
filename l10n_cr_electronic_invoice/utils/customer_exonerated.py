# -*- coding: utf-8 -*-

from odoo import _
import requests
from datetime import datetime, date
url = 'https://api.hacienda.go.cr/fe/ex?autorizacion='

def find_data(self):
    res = {}
    url_compound = url + self.numero_documento
    result = requests.get(url_compound)
    if result.status_code == 200:
        json = result.json()
        identification = json['identificacion']
        numeroDocumento = json['numeroDocumento']
        if self.vat != False and self.vat != identification:
            res['warning'] = {'title': _('Ups'), 'message': _(
                'El número de identificación encontrado, no conincide con el número de documento del cliente.')}
            return res

        code_type_exoneration = json['tipoDocumento']['codigo']
        type_ex = self.env['aut.ex'].sudo().search([('code', '=', code_type_exoneration)])
        if not type_ex:
            res['warning'] = {'title': _('Ups'), 'message': _(
                'No se encuentra el tipo de exoneración. Contacte al administrador del sistema!')}
            return res
        institution_name = json['nombreInstitucion']
        fecha_emision = json['fechaEmision']
        fecha_vencimiento = json['fechaVencimiento']
        percentage_exoneration = json['porcentajeExoneracion']
        # tax = percentage_exoneration
        tax = self.env['account.tax'].sudo().search([('percentage_exoneration', '=', percentage_exoneration)])
        if not tax:
            res['warning'] = {'title': _('Ups'), 'message': _(
                'No se encontró un impuesto en el sistema con el porcentage de exoneración de: ' + str(
                    percentage_exoneration))}
            return res

        cabys_ids = False
        if json['poseeCabys']:
            cabys_ids = self.env['cabys'].sudo().search([('code', '=', json['poseeCabys'])]).ids


        data = {
            'partner_id': self.partner_id.id,
            'vat': self.vat,
            'numero_documento': numeroDocumento,
            'tax_id': tax.id,
            'porcentaje_exoneracion': percentage_exoneration,
            'cabys_ids': cabys_ids,
            'tipo_documento': type_ex,
            'fecha_emision': datetime.datetime.strptime(fecha_emision, '%Y-%m-%dT%H:%M:%S'),
            'fecha_vencimiento': datetime.datetime.strptime(fecha_vencimiento, '%Y-%m-%dT%H:%M:%S'),
            'institucion': institution_name,
            'date_issue': datetime.strptime(fecha_emision[0:10], '%Y-%m-%d').date(),
            'date_expiration': datetime.strptime(fecha_vencimiento[0:10], '%Y-%m-%d').date(),
        }

        return data

        # partner_tax = self.env['res.partner.tax'].sudo().search(
        #     ['|', ('partner_id', '=', self.id), ('vat', '=', self.vat)])
        # if not partner_tax:
        #     self.env['res.partner.tax'].sudo().create({'partner_id': self.id, 'vat': self.vat, 'tax_id': tax.id})
        # else:
        #     partner_tax.sudo().write({'tax_id': tax.id})
        # res['warning'] = {'title': _('Bien!'), 'message': _('Datos encontrados!')}
        # return res


    else:
        res['warning'] = {'title': _('Ups'), 'message': _('Documento de exoneración no encontrado !')}
        return res