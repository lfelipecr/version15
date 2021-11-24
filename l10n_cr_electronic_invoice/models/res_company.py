from odoo import _, fields, models

from .. import cr_edi

_TIPOS_CONFIRMACION = (
    # Provides listing of types of comprobante confirmations
    (
        "CCE_sequence_id",
        "account.invoice.supplier.accept.",
        "Supplier invoice acceptance sequence",
    ),
    (
        "CPCE_sequence_id",
        "account.invoice.supplier.partial.",
        "Supplier invoice partial acceptance sequence",
    ),
    (
        "RCE_sequence_id",
        "account.invoice.supplier.reject.",
        "Supplier invoice rejection sequence",
    ),
    (
        "FEC_sequence_id",
        "account.invoice.supplier.reject.",
        "Supplier electronic purchase invoice sequence",
    ),
)


class Company(models.Model):
    _name = "res.company"
    _inherit = [
        "res.company",
        "mail.thread",
    ]

    commercial_name = fields.Char()
    pos_activity_id = fields.Many2one(
        comodel_name="economic_activity",
        string="Economic activity POS",
    )
    signature = fields.Binary(
        string="Cryptographic Key",
    )
    identification_id = fields.Many2one(
        comodel_name="identification.type",
        string="ID Type",
    )
    frm_ws_identificador = fields.Char(
        string="Electronic Invoice User",
    )
    frm_ws_password = fields.Char(
        string="Electronic Invoice Password",
    )
    frm_ws_ambiente = fields.Selection(
        selection=[
            ("api-stag", _("Tests")),
            ("api-prod", _("Production")),
        ],
        string="Environment",
        help="It is the environment in which the certificate is being updated. For the quality environment (Test), for the production environment (Production).",
    )
    frm_pin = fields.Char(
        string="Pin",
        help="It is the pin corresponding to the certificate",
    )
    sucursal_MR = fields.Integer(
        string="Subsidairy for MR sequences",
        default="1",
    )
    terminal_MR = fields.Integer(
        string="Terminal for MR sequences",
        default="1",
    )
    CCE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence Acceptance",
        help="Confirmation sequence of acceptance of electronic receipt. Leave blank and the system will automatically create it for you.",
        copy=False,
    )
    CPCE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Partial Sequence",
        help="Confirmation sequence of partial acceptance of electronic voucher. Leave blank and the system will automatically create it for you.",
        copy=False,
    )
    RCE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Reject Sequence",
        help="Sequence of confirmation of rejection of electronic voucher. Leave blank and the system will automatically create it for you.",
        copy=False,
    )
    FEC_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence of Electronic Purchase Invoices",
        copy=False,
    )

    def try_create_confirmation_sequeces(self):
        """Try to automatically add the Comprobante Confirmation sequence to the company.
        It will first check if sequence already exists before attempt to create. The s
        equence is coded with the following syntax:
            account.invoice.supplier.<tipo>.<company_name>
        where tipo is: accept, partial or reject, and company_name is either the first word
        of the name or commercial name.
        """
        company_subname = self.commercial_name
        if not company_subname:
            company_subname = self.name
        company_subname = company_subname.split(" ")[0].lower()
        ir_sequence = self.env["ir.sequence"]
        to_write = {}
        for field, seq_code, seq_name in _TIPOS_CONFIRMACION:
            if not getattr(self, field, None):
                seq_code += company_subname
                seq = self.env.ref(seq_code, raise_if_not_found=False) or ir_sequence.create(
                    {
                        "name": seq_name,
                        "code": seq_code,
                        "implementation": "standard",
                        "padding": 10,
                        "use_date_range": False,
                        "company_id": self.id,
                    }
                )
                to_write[field] = seq.id

        if to_write:
            self.write(to_write)

    def get_token(self):
        self.ensure_one()
        token = cr_edi.auth.get_token(
            internal_id=self.id,
            username=self.frm_ws_identificador,
            password=self.frm_ws_password,
            client_id=self.frm_ws_ambiente,
        )
        return token
