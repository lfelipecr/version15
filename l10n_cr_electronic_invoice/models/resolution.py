from odoo import fields, models


class Resolution(models.Model):  # TODO Is necessary?
    _name = "resolution"
    _description = "Resolution"

    active = fields.Boolean(
        default=True,
    )
    name = fields.Char()
    date_resolution = fields.Date()
