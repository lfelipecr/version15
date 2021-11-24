from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    county_id = fields.Many2one(
        comodel_name="res.country.county",
    )
    district_id = fields.Many2one(
        comodel_name="res.country.district",
    )
    neighborhood_id = fields.Many2one(
        comodel_name="res.country.neighborhood",
    )
