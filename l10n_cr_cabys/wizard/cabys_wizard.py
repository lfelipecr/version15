# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date, formatLang

from collections import defaultdict
from itertools import groupby
import json
class CabysWizard(models.TransientModel):
    _name = 'cabys.wizard'
    _description = 'Obtener cabys según la compañia seleccionada'

    company_id = fields.Many2one('res.company', required=True,  default=lambda self: self.env.company, string=u'Compañia')



    def get_cabys(self):
        objCabys = self.env['cabys'].sudo()
        objCabys.update_tax_ids(self.company_id)



