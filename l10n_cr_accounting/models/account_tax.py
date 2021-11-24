from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    tax_code = fields.Char()
    iva_tax_desc = fields.Char(
        string="VAT rate",
        default="N/A",
    )
    iva_tax_code = fields.Char(
        string="VAT Rate Code",
        default="N/A",
    )
    has_exoneration = fields.Boolean(
        string="Tax Exonerated",
    )
    percentage_exoneration = fields.Integer()
    tax_root = fields.Many2one(
        comodel_name="account.tax",
    )

    @api.onchange("tax_root")
    def _onchange_tax_root(self):
        self.tax_compute_exoneration()

    @api.constrains("percentage_exoneration")
    def _check_percentage_exoneration(self):
        for tax in self:
            if tax.percentage_exoneration > 100:
                raise UserError(_("The percentage cannot be greater than 100"))

    @api.depends("percentage_exoneration")
    def tax_compute_exoneration(self):
        for tax in self:
            if tax.tax_root:
                _tax_amount = tax.tax_root.amount / 100
                _procentage = tax.percentage_exoneration / 100
                tax.amount = (_tax_amount * (1 - _procentage)) * 100
