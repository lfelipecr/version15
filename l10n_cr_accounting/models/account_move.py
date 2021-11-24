import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    # TODO: check usage of next field
    reference_code_id = fields.Many2one(
        comodel_name="reference.code",
        readonly=True,
        states={"draft": [("readonly", False)]},
        string=u'Tipo nota crédito'
    )
    payment_methods_id = fields.Many2one(
        comodel_name="payment.methods",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # TODO: check usage of next field
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        string="Invoice Reference",
    )
    invoice_amount_text = fields.Char(
        compute="_compute_invoice_amount_text",
    )
    total_services_taxed = fields.Float(
        compute="_compute_total_services_taxed",
    )
    total_services_exempt = fields.Float(
        compute="_compute_total_services_exempt",
    )
    total_products_taxed = fields.Float(
        compute="_compute_total_products_taxed",
    )
    total_products_exempt = fields.Float(
        compute="_compute_total_products_exempt",
    )
    total_taxed = fields.Float(
        compute="_compute_total_taxed",
    )
    total_exempt = fields.Float(
        compute="_compute_total_exempt",
    )
    total_sale = fields.Float(
        compute="_compute_total_sale",
    )
    total_discount = fields.Float(
        compute="_compute_total_discount",
    )
    total_others = fields.Float(
        compute="_compute_total_others",
    )
    purchase_type = fields.Selection(
        selection=[
            ("purchase", _("Purchase")),
            ("asset", _("Asset")),
            ("service", _("Service")),
            ("no_subject", _("No subject")),
        ],
    )

    def _get_activity_id(self):
        return [("id", "in", self.env.user.company_id.activity_ids.ids)]

    def _default_activity_id(self):
        company_id = self.company_id
        if not company_id:
            company_id = self.env.user.company_id
        if company_id.def_activity_id:
            return company_id.def_activity_id
        else:
            return False

    activity_id = fields.Many2one(
        comodel_name="economic_activity",
        ondelete="restrict",
        domain=_get_activity_id,
        default=_default_activity_id,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    tipo_documento = fields.Selection(
        selection=[
            ("FE", _("Factura electrónica")),
            ("FEE", _("Factura electrónica de exportación")),
            ("TE", _("Tiquete electrónico")),
            ("NC", _("Nota de crédito")),
            ("ND", _("Nota de débito")),
            ("CCE", _("Aceptación MR")),
            ("CPCE", _("Aceptación parcial de MR")),
            ("RCE", _("Rechazo MR")),
            ("FEC", _("Factura electrónica de compra")),
        ],
        default="FE",
        help="Indicates the type of document according to the classification of the Ministry of Finance",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.depends("invoice_line_ids")
    def _compute_total_services_taxed(self):
        for record in self:
            record.total_services_taxed = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type == "service" and l.tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("invoice_line_ids")
    def _compute_total_services_exempt(self):
        for record in self:
            record.total_services_exempt = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type == "service" and not l.tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("invoice_line_ids")
    def _compute_total_products_taxed(self):
        for record in self:
            record.total_products_taxed = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type != "service" and l.tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("invoice_line_ids")
    def _compute_total_products_exempt(self):
        for record in self:
            record.total_products_exempt = sum(
                record.invoice_line_ids.filtered(
                    lambda l: l.product_id.type != "service" and not l.tax_ids
                ).mapped("price_subtotal")
            )

    @api.depends("total_products_taxed", "total_services_taxed")
    def _compute_total_taxed(self):
        for record in self:
            record.total_taxed = record.total_products_taxed + record.total_services_taxed

    @api.depends("total_products_exempt", "total_services_exempt")
    def _compute_total_exempt(self):
        for record in self:
            record.total_exempt = record.total_products_exempt + record.total_services_exempt

    @api.depends("total_products_taxed", "total_services_taxed")
    def _compute_total_sale(self):
        for record in self:
            record.total_sale = record.total_taxed + record.total_exempt

    def _compute_total_discount(self):
        for record in self:
            record.total_discount = sum(record.invoice_line_ids.mapped("discount_amount"))

    def _compute_total_others(self):
        for record in self:
            record.total_others = 0  # TODO

    def name_get(self):
        """Add amount_untaxed in name_get of invoices"""
        res = super(AccountInvoice, self).name_get()
        if self._context.get("invoice_show_amount"):
            new_res = []
            for (inv_id, name) in res:
                inv = self.browse(inv_id)
                name += _(" Amount w/o tax: {} {}").format(inv.amount_untaxed, inv.currency_id.name)
                new_res.append((inv_id, name))
            return new_res
        else:
            return res

    @api.depends("amount_total")
    def _compute_invoice_amount_text(self):
        for record in self:
            record.invoice_amount_text = record.currency_id.amount_to_text(record.amount_total)
