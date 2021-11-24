from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sale_conditions_id = fields.Many2one(
        comodel_name="sale.conditions",
    )
