# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

IVA_CONDITION = [("gecr", "Genera crédito IVA"),
                  ("crpa", "Genera crédito parcial del IVA"),
                  ("bica", "Bienes de capital"),
                  ("gcnc", "El gasto corriente no genera crédito"),
                  ("prop", "Proporcionalidad"), ]

class AccountInvoice(models.Model):
    _inherit = "account.move"

    has_exoneration = fields.Boolean(default=False, copy=False, related='partner_id.has_exoneration')
    due_exoneration = fields.Date(default=False, copy=False, related='partner_id.date_expiration')
    is_expired = fields.Boolean(compute='computed_expired', store=True, copy=False)
    partner_tax_id = fields.Many2one('account.tax')

    apply_discount_global = fields.Boolean(string='Descuento general ?', states={'draft': [('readonly', False)]},copy=False)
    percentage_discount_global = fields.Float('Descuento',copy=False)
    amount_discount = fields.Monetary('Total descuento',copy=False, store=True, default=0.0)
    re_calcule = fields.Boolean(default=False)
    amount_gravada = fields.Monetary()
    amount_exonerated = fields.Monetary()

    iva_condition = fields.Selection(IVA_CONDITION, string=u"Condición IVA", required=False)


    def _default_date(self):
        return datetime.now().date()

    invoice_date = fields.Date(string='Fecha factura', readonly=True, index=True, copy=False,
                               states={'draft': [('readonly', False)]}, default=_default_date)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        #res = {}
        if self.partner_id and self.partner_id.exoneration_number:
            self.partner_tax_id = self.partner_id.exoneration_number.tax_id
        else:
            self.partner_tax_id = False
            # #partner_tax = self.env['res.partner.tax'].sudo().search(['|',('partner_id', '=', self.partner_id.id),('vat','=',self.partner_id.vat)])
            # # if not partner_tax:
            # #     res['warning'] = {'title': _('Ups'), 'message': _('No se encontró un impuesto en el sistema con el porcentage de exoneración de: ' + str(self.partner_id.tax))}
            # #     return res
            # if partner_tax:
            #
            # else:
            #     self.partner_tax_id = False
    @api.depends('has_exoneration','due_exoneration')
    def computed_expired(self):
        for inv in self:
            inv.is_expired = False
            if inv.partner_id:
                if inv.has_exoneration and inv.due_exoneration:
                    inv.is_expired = self.func_expiration(inv.due_exoneration)

    # @api.onchange('percentage_discount_global')
    # def _onchange_percentage_discount_global(self):
    #     for inv in self:
    #         if inv.apply_discount_global:
    #             if inv.percentage_discount_global < 0.0:
    #                 raise UserError(_('El porcentaje debe ser mayor a 0'))
    #             inv.calc_discount()

    @api.onchange('has_exoneration', 'partner_tax_id', 'due_exoneration')
    def _onchange_sale_tax(self):
        for inv in self:
            inv.is_expired = False
            if inv.has_exoneration and inv.partner_tax_id:
                inv.is_expired = self.func_expiration(inv.due_exoneration)
                for line in inv.invoice_line_ids:
                    line.tax_id = {}
                    line.tax_id = inv.partner_tax_id


    def _percent_discount(self,p,t):
        if t>0:
            return round(p/t,2)
        return 0

    def calc_discount(self):
        for inv in self:
            inv.re_calcule = False
            if inv.apply_discount_global:
                if inv.percentage_discount_global > 0.0:
                    if inv.invoice_line_ids:
                        total = len(inv.invoice_line_ids.ids)
                        percentage_discount = self._percent_discount(inv.percentage_discount_global,total)
                        array = []
                        for line in inv.invoice_line_ids:
                            if line.product_id:
                                if len(line.ids)>0:
                                    ids = line.ids[0]
                                else:
                                    ids = line.id.ref
                                array.append((1, ids, {'discount': percentage_discount}))
                        if len(array) > 0:
                            inv.write({'invoice_line_ids': array})


    def change_color_line(self):
        for inv in self:
            for x in inv.invoice_line_ids:
                x.write({'change_color': False})

            for line in inv.invoice_line_ids:
                for line2 in inv.invoice_line_ids:
                    if not line.change_color:
                        if line != line2 and line.product_id.id == line2.product_id.id:
                            line2.write({'change_color': True})



        # for inv in self:
        #     for line in inv.invoice_line_ids:
        #         for line2 in inv.invoice_line_ids:
        #             if not line2.change_color:
        #                 if line!=line2 and line.product_id.id == line2.product_id.id:
        #                     line2.write({'change_color': True})
        #
        #     # for l in inv.invoice_line_ids:
        #     #     sw=0
        #     #
        #     #     for l2 in inv.invoice_line_ids:
        #     #         if l.product_id.id == l2.product_id.id and l.id != l2.id and not l2.change_color and not l.change_color:
        #     #             sw=1
        #     #             break
        #     #     if sw==1:
        #     #         l2.write({'change_color': True})


    def _check_percentage_global(self):
        for inv in self:
            inv.re_calcule = False
            if inv.apply_discount_global:
                if len(inv.invoice_line_ids) > 0:
                    per = inv._percent_discount(inv.percentage_discount_global, len(inv.invoice_line_ids.ids))
                    sw = 0
                    for line in inv.invoice_line_ids:
                        if line.discount != per:
                            sw = 1
                            break
                    if sw == 1:
                        inv.re_calcule = True
                    else:
                        inv.re_calcule = False

    def write(self, vals):
        r = super(AccountInvoice, self).write(vals)
        self.change_color_line()
        return r

    # def _move_autocomplete_invoice_lines_values(self):
    #     r = super(AccountInvoice, self)._move_autocomplete_invoice_lines_values()
    #     if self.apply_discount_global and self.percentage_discount_global > 0.0:
    #         r['re_calcule'] = self._check_percentage_global()
    #     return r


    def func_expiration(self, date_due):
        is_expired = False
        if date.today() > date_due:
            is_expired = True
        return is_expired

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        self.compute_amount_exonerated()
        self.compute_amount_discount()
        self._check_percentage_global()

    def compute_amount_exonerated(self):
        for move in self:
            if move.has_exoneration and move.partner_tax_id:
                amount_exonerated = 0.0
                amount_gravada = 0.0

                amount_gravada = move.exoneration_cal() * move.amount_untaxed
                amount_exonerated = move.amount_untaxed - amount_gravada

                move.amount_gravada = amount_gravada
                move.amount_exonerated = amount_exonerated


                # tax_exonerated = move.partner_tax_id.percentage_exoneration
                # amount_exonerated = move.amount_untaxed * (tax_exonerated / 100)
                # move.amount_exonerated = amount_exonerated

    def compute_amount_discount(self):
        for move in self:
            if move.apply_discount_global and move.percentage_discount_global>0.0:
                amount_discount = 0.0
                amount_discount = sum(line.discount_amount for line in move.line_ids)
                move.amount_discount = amount_discount




    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        ''' During the create of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   The list of values passed to the 'create' method.
        :return:            Modified list of values.
        '''
        new_vals_list = []
        for vals in vals_list:
            if not vals.get('invoice_line_ids'):
                new_vals_list.append(vals)
                continue
            if vals.get('line_ids'):
                vals.pop('invoice_line_ids', None)
                new_vals_list.append(vals)
                continue
            if not vals.get('move_type') and not self._context.get('default_move_type'):
                vals.pop('invoice_line_ids', None)
                new_vals_list.append(vals)
                continue
            vals['move_type'] = vals.get('move_type', self._context.get('default_move_type', 'entry'))
            if not vals['move_type'] in self.get_invoice_types(include_receipts=True):
                new_vals_list.append(vals)
                continue

            vals['line_ids'] = vals.pop('invoice_line_ids')

            if vals.get('invoice_date') and not vals.get('date'):
                vals['date'] = vals['invoice_date']

            ctx_vals = {'default_move_type': vals.get('move_type') or self._context.get('default_move_type')}
            if vals.get('currency_id'):
                ctx_vals['default_currency_id'] = vals['currency_id']
            if vals.get('journal_id'):
                ctx_vals['default_journal_id'] = vals['journal_id']
                # reorder the companies in the context so that the company of the journal
                # (which will be the company of the move) is the main one, ensuring all
                # property fields are read with the correct company
                journal_company = self.env['account.journal'].browse(vals['journal_id']).company_id
                allowed_companies = self._context.get('allowed_company_ids', journal_company.ids)
                reordered_companies = sorted(allowed_companies, key=lambda cid: cid != journal_company.id)
                ctx_vals['allowed_company_ids'] = reordered_companies
            self_ctx = self.with_context(**ctx_vals)
            new_vals = self_ctx._add_missing_default_values(vals)

            move = self_ctx.new(new_vals)
            new_vals_list.append(move._move_autocomplete_invoice_lines_values())

        return new_vals_list

        # Nuevo 17-11-2021

    def action_quit_lines(self):
        for record in self:
            if record.invoice_line_ids:
                for line in record.invoice_line_ids:
                    record.write({'invoice_line_ids': [(3, line.id)]})

            # if record.amount_tax_electronic_invoice:
            #     record.amount_tax_electronic_invoice = 0.0
            # if record.amount_total_electronic_invoice:
            #     record.amount_total_electronic_invoice = 0.0

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    change_color = fields.Boolean()

    def _get_computed_taxes(self):
        tax_ids = super(AccountMoveLine, self)._get_computed_taxes()
        if self.move_id.is_sale_document(include_receipts=True):
            if self.move_id.partner_tax_id and self.move_id.has_exoneration:
                tax_ids = self.move_id.partner_tax_id
        return tax_ids

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(AccountMoveLine, self)._onchange_product_id()

        lines = self.move_id.invoice_line_ids - self
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
        #         if len(line.move_id.line_ids) > 0:
        #             for x in line.move_id.line_ids:
        #                 if x.product_id.id == line.product_id.id and x.sequence != line.sequence:
        #                     line.change_color = True
        #                     break

