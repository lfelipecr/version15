from odoo import fields, models


class AutEx(models.Model):
    _name = "aut.ex"
    _description = "Autorization Model"

    active = fields.Boolean(
        default=True,
    )
    code = fields.Char()
    name = fields.Char()
