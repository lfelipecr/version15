from odoo import fields, models


class EconomicActivity(models.Model):
    _name = "economic_activity"
    _description = "Economic Activity"

    active = fields.Boolean(
        default=True,
    )
    code = fields.Char()
    name = fields.Char()
    description = fields.Char()
