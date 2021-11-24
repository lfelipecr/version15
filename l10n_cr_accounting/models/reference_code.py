from odoo import fields, models


class ReferenceCode(models.Model):
    _name = "reference.code"
    _description = "Reference Code"

    active = fields.Boolean(
        default=True,
    )
    code = fields.Char()
    name = fields.Char()
