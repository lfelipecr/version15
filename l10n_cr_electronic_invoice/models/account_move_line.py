from odoo import fields, models, api


class InvoiceLineElectronic(models.Model):
    _inherit = "account.move.line"

    tariff_head = fields.Char(
        string="Tariff heading for export invoice",
        required=False,
    )

    def _onchange_balance(self):
        for line in self:
            if line.currency_id:
                continue
            if not line.move_id.is_invoice(include_receipts=True):
                continue
            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())


    info_json = fields.Text('Información')
