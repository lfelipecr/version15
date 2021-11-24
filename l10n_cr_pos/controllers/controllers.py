#-*- coding: utf-8 -*-
from odoo import http

from odoo.http import request, Response
import json

class L10nCrPosSale(http.Controller):

    @http.route(['/shop/confirm_quotation'], type='http', auth="public", methods=['POST'], website=False, csrf=False)
    def get_order(self, id=None):
        pos_order = request.env['pos.order'].search([('pos_reference','like',id)])
        value = {}
        if pos_order:
            value = {
                'number_electronic': pos_order.number_electronic,
                'sequence': pos_order.sequence,
                'tipo_documento': pos_order.tipo_documento,
            }

        return json.dumps(value)
