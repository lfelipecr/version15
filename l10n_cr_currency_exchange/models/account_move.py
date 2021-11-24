from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    currency_rate_usd_crc = fields.Float(
        compute="_compute_currency_rate_usd_crc",
        store=True,
        string="USD/CRC Rate",
    )

    @api.depends("invoice_date", "company_id")
    def _compute_currency_rate_usd_crc(self):
        crc_currency = self.env.ref("base.CRC")
        usd_currency = self.env.ref("base.USD")
        for invoice in self:
            if not (invoice.invoice_date and invoice.company_id):
                continue
            invoice.currency_rate_usd_crc = usd_currency._convert(
                1, crc_currency, invoice.company_id, invoice.invoice_date
            )
