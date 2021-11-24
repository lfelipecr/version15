# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_exoneration = fields.Boolean(default=False, copy=False, related='partner_id.has_exoneration')
    due_exoneration = fields.Date(default=False, copy=False, related='partner_id.date_expiration')
    is_expired = fields.Boolean(compute='computed_expired', store=True, copy=False)
    partner_tax_id = fields.Many2one('account.tax')

    apply_discount_global = fields.Boolean(string='Descuento general ?', states={'draft': [('readonly', False)]},copy=False)
    percentage_discount_global = fields.Float('Descuento', copy=False)
    amount_discount = fields.Monetary('Total descuento', copy=False, store=True, default=0.0)
    re_calcule = fields.Boolean(default=False)
    amount_gravada = fields.Monetary()
    amount_exonerated = fields.Monetary()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id and self.partner_id.exoneration_number:
            self.partner_tax_id = self.partner_id.exoneration_number.tax_id
        else:
            self.partner_tax_id = False

    @api.depends('has_exoneration', 'due_exoneration')
    def computed_expired(self):
        for order in self:
            order.is_expired = False
            if order.partner_id:
                if order.has_exoneration and order.due_exoneration:
                    order.is_expired = self.func_expiration(order.due_exoneration)


    @api.onchange('has_exoneration', 'partner_tax_id', 'due_exoneration')
    def _onchange_sale_tax(self):
        for order in self:
            order.is_expired = False
            if order.has_exoneration and order.partner_tax_id:
                order.is_expired = self.func_expiration(order.due_exoneration)
                for line in order.order_line:
                    line.tax_id = {}
                    line.tax_id = order.partner_tax_id


    def _percent_discount(self, p, t):
        if t > 0:
            return round(p / t, 2)
        return 0

    def calc_discount(self):
        for order in self:
            order.re_calcule = False
            if order.apply_discount_global:
                if order.percentage_discount_global > 0.0:
                    if order.order_line:
                        total = len(order.order_line.ids)
                        percentage_discount = self._percent_discount(order.percentage_discount_global, total)
                        array = []
                        for line in order.order_line:
                            if line.product_id:
                                if len(line.ids) > 0:
                                    ids = line.ids[0]
                                else:
                                    ids = line.id.ref
                                array.append((1, ids, {'discount': percentage_discount}))
                        if len(array) > 0:
                            order.write({'order_line': array})

    def change_color_line(self):
        for order in self:
            for x in order.order_line:
                x.write({'change_color': False})

            for line in order.order_line:
                for line2 in order.order_line:
                    if not line.change_color:
                        if line != line2 and line.product_id.id == line2.product_id.id:
                            line2.write({'change_color': True})

    def _check_percentage_global(self):
        for order in self:
            if len(order.order_line) > 0:
                per = order._percent_discount(order.percentage_discount_global, len(order.order_line.ids))
                sw = 0
                for line in order.order_line:
                    if line.discount != per:
                        sw = 1
                        break
                if sw == 1:
                    order.re_calcule = True
                else:
                    order.re_calcule = False

    def write(self, vals):
        r = super(SaleOrder, self).write(vals)
        self.change_color_line()
        return r

    # @api.depends('order_line.price_total')
    # def _amount_all(self):
    #     super(SaleOrder, self)._amount_all()
    #     for order in self:
    #         if order.apply_discount_global and order.percentage_discount_global > 0.0:
    #             res = order._check_percentage_global()
    #             order.update({'re_calcule': res})

    def func_expiration(self, date_due):
        is_expired = False
        if date.today() > date_due:
            is_expired = True
        return is_expired

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['apply_discount_global'] = self.apply_discount_global
        res['percentage_discount_global'] = self.percentage_discount_global
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    change_color = fields.Boolean()


    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(line.order_partner_id.id)
            # If company_id is set, always filter taxes by the company
            if line.order_id.partner_tax_id and line.order_id.partner_id.has_exoneration:
                taxes = line.order_id.partner_tax_id.filtered(lambda t: t.company_id == line.env.company)
            else:
                taxes = line.product_id.taxes_id.filtered(lambda t: t.company_id == line.env.company)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id)

    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()

        lines = self.order_id.order_line - self
        for line in lines:
            if self.product_id.id == line.product_id.id and (self.id != line.id) and line.name != False:
                if self.change_color:
                    self.change_color = False
                else:
                    self.change_color = True
                break

        # for line in self:
        #     if line.product_id:
        #         line.change_color = False
        #
        #         if len(line.order_id.order_line) > 0:
        #             for x in line.order_id.order_line:
        #                 # if x.product_id.id == line.product_id.id and (x.pool != line.id or x.sequence != line.sequence):
        #                 #     line.change_color = True
        #                 #     break
        #                 a=x
        #

