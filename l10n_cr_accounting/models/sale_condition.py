from odoo import fields, models


class SaleConditions(models.Model):
    _name = "sale.conditions"
    _description = "Sale Conditions"

    active = fields.Boolean(
        required=False,
        default=True,
    )
    sequence = fields.Char(
        required=False,
    )
    name = fields.Char(
        required=False,
    )
    notes = fields.Text(
        required=False,
    )
