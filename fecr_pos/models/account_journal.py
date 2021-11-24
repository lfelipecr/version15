from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    payment_method_id = fields.Many2one(
        comodel_name="payment.methods",
        string="Payment Methods",
        required=False,
    )
