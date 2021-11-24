from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    county_id = fields.Many2one(
        comodel_name="res.country.county",
    )
    district_id = fields.Many2one(
        comodel_name="res.country.district",
    )
    neighborhood_id = fields.Many2one(
        comodel_name="res.country.neighborhood",
    )
