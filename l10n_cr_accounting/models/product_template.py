from odoo import api, fields, models


class ProductElectronic(models.Model):
    _inherit = "product.template"

    @api.model
    def _default_code_type_id(self):
        code_type_id = self.env["code.type.product"].search([("code", "=", "04")], limit=1)
        return code_type_id or False

    commercial_measurement = fields.Char(  # TODO necessary?
        string="Commercial Measurement Unit",
        required=False,
    )
    code_type_id = fields.Many2one(  # TODO Is this necessary?
        comodel_name="code.type.product",
        required=False,
        default=_default_code_type_id,
    )
