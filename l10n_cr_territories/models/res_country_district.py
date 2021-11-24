from odoo import fields, models


class ResCountryDistrict(models.Model):
    _name = "res.country.district"
    _description = "Country State County District Subdivision"
    _order = "name"

    code = fields.Char(
        required=True,
    )
    county_id = fields.Many2one(
        comodel_name="res.country.county",
        required=True,
    )
    name = fields.Char(
        required=True,
    )
