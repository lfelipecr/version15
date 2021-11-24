# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    reference_code_id = fields.Many2one('reference.code',string=u'Tipo nota crédito',required=True)

    @api.onchange('reference_code_id')
    def _onchange_reference_code_id(self):
        if self.reference_code_id:
            self.reason = self.reference_code_id.name

    def _prepare_default_reversal(self, move):
        reverse_date = self.date if self.date_mode == 'custom' else move.date
        return {
            'ref': _('Rectificativa de: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
                   if self.reason
                   else _('Rectificativa de: %s', move.name),
            'date': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': True if reverse_date > fields.Date.context_today(self) else False,
            'reference_code_id': self.reference_code_id.id,
            'invoice_id':  move.id,
            'tipo_documento': 'NC',
            'invoice_payment_term_id': move.invoice_payment_term_id.id,
        }
