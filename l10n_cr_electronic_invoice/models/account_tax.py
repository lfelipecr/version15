# -*- coding: utf-8 -*-

from odoo import api, fields, models


classification_type = [
    ('none','Ninguna'),
    ('exempt','Exento'),
    ('no_hold','No Sujeta'),
    ('exonerated','Exonerada')
]

class AccountJournalInherit(models.Model):
    _inherit = "account.tax"

    classification_type = fields.Selection(selection=classification_type, string='Clasificación', default='none')

    @api.onchange('classification_type')
    def _onchange_classification_type(self):
        for record in self:
            if record.classification_type:
                if record.classification_type == 'exonerated':
                    record.has_exoneration = True
                else:
                    record.has_exoneration = False
