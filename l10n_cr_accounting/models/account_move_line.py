from odoo import api, fields, models


class MoveLine(models.Model):
    _inherit = "account.move.line"

    total_amount = fields.Float()
    discount_note = fields.Char()
    third_party_id = fields.Many2one(
        comodel_name="res.partner",
    )
    categ_name = fields.Char(
        related="product_id.categ_id.name",
    )
    product_code = fields.Char(
        related="product_id.default_code",
    )
    # no_discount_amount = fields.Monetary(
    #     compute="_compute_discount_amount",
    # )
    # discount_amount = fields.Monetary(
    #     compute="_compute_discount_amount",
    # )
    no_discount_amount = fields.Float(
        compute="_compute_discount_amount",store=True
    )
    discount_amount = fields.Float(
        compute="_compute_discount_amount",store=True
    )

    purchase_type = fields.Selection(
        related="move_id.purchase_type",
        store=True,
    )
    type_tax_use = fields.Selection(
        related="tax_line_id.type_tax_use",
        store=True,
    )
    activity_id = fields.Many2one(
        related="move_id.activity_id",
        store=True,
    )
    amount_sale = fields.Monetary(
        compute="_compute_amount_sale",
        store=True,
    )
    state = fields.Selection(
        related="move_id.state",
    )
    total_tax = fields.Float(
        compute="_compute_total_tax",
        store=True,
    )

    @api.depends("tax_ids", "price_subtotal")
    def _compute_total_tax(self):
        for line in self:
            line.total_tax = sum(
                line.tax_ids.mapped(lambda tax: tax.amount / 100 * line.price_subtotal)
            )

    @api.depends("price_total", "tax_base_amount")
    def _compute_amount_sale(self):
        for record in self:
            record.amount_sale = record.tax_base_amount + record.price_total

    @api.depends("quantity", "price_unit", "discount")
    def _compute_discount_amount(self):
        for record in self:
            record.no_discount_amount = record.quantity * record.price_unit
            record.discount_amount = record.no_discount_amount * record.discount / 100
