from odoo import fields, models


class ProductElectronic(models.Model):
    _inherit = "product.template"

    tariff_head = fields.Char(
        string="Tariff item for export invoice",
        required=False,
    )
