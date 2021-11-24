# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    payment_method_id = fields.Many2one('payment.methods',string=u'Método de pago')
    account_payment_term_id = fields.Many2one('account.payment.term',string=u'Término de pago')
    is_refund = fields.Boolean(default=False, string=u'Usado para devolución')

    @api.onchange("payment_method_id")
    def _onchange_payment_method_id(self):
        for payment in self:
            if payment.payment_method_id:
                payment.name = payment.payment_method_id.name


