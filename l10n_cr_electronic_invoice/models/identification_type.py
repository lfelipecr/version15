from odoo import fields, models


class IdentificationType(models.Model):
    _name = "identification.type"
    _description = "Identification Type"

    code = fields.Char()
    name = fields.Char()
    notes = fields.Text()
