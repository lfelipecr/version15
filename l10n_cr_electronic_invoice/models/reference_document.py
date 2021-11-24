from odoo import fields, models


class ReferenceDocument(models.Model):
    _name = "reference.document"
    _description = "Reference Document"

    active = fields.Boolean(
        default=True,
    )
    code = fields.Char()
    name = fields.Char()
