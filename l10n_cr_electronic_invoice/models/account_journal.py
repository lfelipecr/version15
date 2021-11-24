from odoo import api, fields, models


class AccountJournalInherit(models.Model):
    _inherit = "account.journal"

    sucursal = fields.Integer(
        string="Sucursal",
        default="1",
    )
    terminal = fields.Integer(
        string="Terminal",
        default="1",
    )
    FE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Electronic Invoice Sequence",
    )
    TE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Electronic Ticket Sequence",
    )
    FEE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence of Electronic Export Invoices",
    )
    NC_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Sequence of Electronic Credit Notes",
    )
    ND_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Electronic Debit Notes Sequence",
    )
    to_process = fields.Boolean(
        default=True,
        help="If is checked, the documents related to this journal will be sended to the API (staging or production, based on company configuration)",
    )

    sequence_id = fields.Many2one('ir.sequence', string='Secuencia.')
    sequence_refund_id = fields.Many2one('ir.sequence', string='Secuencia Rect.')

    @api.model
    def set_sequences(self):
        # Nuevo 2021-10-21
        self_sequence = self.env["ir.sequence"].sudo()
        for record in self.sudo().search([]):
            company_ids = self.env['res.company'].sudo().search([])
            if company_ids:
                for company_id in company_ids:
                    s = self_sequence.search([("code", "=", "sequence.normal.journal.FACT"), ('company_id', '=', company_id.id)], limit=1)
                    if s and record.company_id.id == company_id.id and not record.sequence_id:
                        record.sequence_id = s

                    rs = self_sequence.search([("code", "=", "sequence.normal.journal.RFACT"), ('company_id', '=', company_id.id)], limit=1)
                    if rs and record.company_id.id == company_id.id and not record.sequence_refund_id:
                        record.sequence_refund_id = rs
        # for record in self.search([]):
        #     record.FE_sequence_id = self.env["ir.sequence"].search(
        #         [("code", "=", "sequece.FE")], limit=1
        #     )
        #     record.TE_sequence_id = self.env["ir.sequence"].search(
        #         [("code", "=", "sequece.TE")], limit=1
        #     )
        #     record.FEE_sequence_id = self.env["ir.sequence"].search(
        #         [("code", "=", "sequece.FEE")], limit=1
        #     )
        #     record.NC_sequence_id = self.env["ir.sequence"].search(
        #         [("code", "=", "sequece.NC")], limit=1
        #     )
        #     record.ND_sequence_id = self.env["ir.sequence"].search(
        #         [("code", "=", "sequece.ND")], limit=1
        #     )

