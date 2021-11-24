from odoo import fields, models


class ResCountryCounty(models.Model):
    _name = "res.country.county"
    _description = "Country State County Subdivision"
    _order = "name"

    code = fields.Char(
        required=True,
    )
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        required=True,
    )
    name = fields.Char(
        required=True,
    )
