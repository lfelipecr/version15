import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _name = "res.company"
    _inherit = [
        "res.company",
        "mail.thread",
    ]

    activity_ids = fields.Many2many(
        comodel_name="economic_activity",
        string="Economic activities",
        required=True,
    )

    def_activity_id = fields.Many2one(
        comodel_name="economic_activity",
        string="Default Economic activity",
        required=True, store=True
    )
