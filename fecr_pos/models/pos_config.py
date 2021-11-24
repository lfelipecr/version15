from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    sucursal = fields.Integer(
        string="Sucursal",
        required=False,
        default="1",
    )
    terminal = fields.Integer(
        string="Terminal",
        required=False,
        default="1",
    )
    FE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Secuencia de Facturas Electrónicas",
        required=False,
    )
    NC_sequence_id = fields.Many2one(
        oldname="return_sequence_id",
        comodel_name="ir.sequence",
        string="Secuencia de Notas de Crédito Electrónicas",
        required=False,
    )
    TE_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Secuencia de Tiquetes Electrónicos",
        required=False,
    )

    @api.model
    def set_sequences(self):
        for record in self.search([]):
            record.FE_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.FE")], limit=1
            )[0]
            record.TE_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.TE")], limit=1
            )[0]
            record.NC_sequence_id = self.env["ir.sequence"].search(
                [("code", "=", "sequece.NC")], limit=1
            )[0]
