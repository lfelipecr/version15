from odoo import models


class PoSOrder(models.Model):
    _inherit = "pos.order"

    def action_pos_order_invoice(self):
        res = super(PoSOrder, self).action_pos_order_invoice()
        if not res:
            return {}
        move_id = self.env["account.move"].browse(res["res_id"])
        move_id.invoice_payment_term_id = self.env["account.payment.term"].search(
            [], limit=1
        )  # TODO check
        return res
