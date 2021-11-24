import logging

from odoo import _, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def action_invoice_sent(self):
        # Old method
        """Send invoice by mail

        Raises:
            UserError: Response XML from Hacienda has not been received
            UserError: Invoice XML has not been generated
            UserError: Partner is not assigned to this invoice
        """
        self.ensure_one()
        if self.invoice_id.move_type == "in_invoice" or self.invoice_id.move_type == "in_refund":
            email_template = self.env.ref(
                "l10n_cr_send_invoice.email_template_invoice_vendor", False
            )
        else:
            email_template = self.env.ref("account.email_template_edi_invoice", False)

        email_template.attachment_ids = [(5)]

        if self.partner_id and self.partner_id.email:

            attachment_search = (
                self.env["ir.attachment"]
                .sudo()
                .search_read(
                    [
                        ("res_model", "=", "account.move"),
                        ("res_id", "=", self.id),
                        ("res_field", "=", "xml_comprobante"),
                    ],
                    limit=1,
                )
            )
            if attachment_search:
                attachment = self.env["ir.attachment"].browse(attachment_search[0]["id"])
                attachment.name = self.fname_xml_comprobante

                attachment_resp_search = (
                    self.env["ir.attachment"]
                    .sudo()
                    .search_read(
                        [
                            ("res_model", "=", "account.move"),
                            ("res_id", "=", self.id),
                            ("res_field", "=", "xml_respuesta_tributacion"),
                        ],
                        limit=1,
                    )
                )

                if attachment_resp_search:
                    attachment_resp = self.env["ir.attachment"].browse(
                        attachment_resp_search[0]["id"]
                    )
                    attachment_resp.name = self.fname_xml_respuesta_tributacion

                    email_template.attachment_ids = [(6, 0, [attachment.id, attachment_resp.id])]

                    email_template.with_context(type="binary", default_type="binary").send_mail(
                        self.id, raise_exception=False, force_send=True
                    )

                    email_template.attachment_ids = [(5)]

                    self.write(
                        {
                            "is_move_sent": True,
                            "state_email": "sent",
                        }
                    )
                else:
                    raise UserError(_("Response XML from Hacienda has not been received"))
            else:
                raise UserError(_("Invoice XML has not been generated"))
        else:
            raise UserError(_("Partner is not assigned to this invoice"))

    def _send_mail(self):
        """If original and response XML attached, send and email to the partner with this files if partner email and tipo_document != FEC

        Raises:
            ValidationError: If no valid email template based on invoice.move_type
        """
        if self.tipo_documento == "FEC" or not (self.partner_id and self.partner_id.email):
            return

        if self.move_type in ("out_invoice", "out_refund"):
            email_template = self.env.ref("account.email_template_edi_invoice", False)
        elif self.move_type in ("in_invoice", "in_refund"):
            email_template = self.env.ref(
                "l10n_cr_send_invoice.email_template_invoice_vendor", False
            )
        if not email_template:
            raise ValidationError(_("No email template"))

        attachment_search = (
            self.env["ir.attachment"]
            .sudo()
            .search_read(
                [
                    ("res_model", "=", "account.move"),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "xml_comprobante"),
                ],
                limit=1,
            )
        )
        if not attachment_search:
            return
        attachment_xml = self.env["ir.attachment"].browse(attachment_search[0]["id"])
        if not attachment_xml:
            return
        # TODO this may be in the attachment creation
        attachment_xml.name = self.fname_xml_comprobante
        attachment_xml.mimetype = "text/xml"

        attachment_response_search = (
            self.env["ir.attachment"]
            .sudo()
            .search_read(
                [
                    ("res_model", "=", "account.move"),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "xml_respuesta_tributacion"),
                ],
                limit=1,
            )
        )
        if not attachment_response_search:
            return
        attachment_xml_response = self.env["ir.attachment"].browse(
            attachment_response_search[0]["id"]
        )
        if not attachment_xml_response:
            return
        # TODO this may be in the attachment creation
        attachment_xml_response.name = self.fname_xml_respuesta_tributacion
        attachment_xml_response.mimetype = "text/xml"

        email_template.attachment_ids = [(6, 0, [attachment_xml.id, attachment_xml_response.id])]
        email_template.with_context(type="binary", default_type="binary").send_mail(
            self.id,
            raise_exception=False,
            force_send=True,
        )
        email_template.attachment_ids = [(5)]
        self.write(
            {
                "is_move_sent": True,
                "state_email": "sent",
            }
        )

    def update_state(self):
        super().update_state()
        if self.state_tributacion == 'aceptado' and self.move_type in ('out_invoice','out_refund','in_invoice'):
            self._send_mail()
