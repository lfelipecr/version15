from odoo import fields, models


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    state_name = fields.Char(
        related="state_id.name",
    )
    country_name = fields.Char(
        related="country_id.name",
    )
    district_name = fields.Char(
        related="district_id.name",
    )
