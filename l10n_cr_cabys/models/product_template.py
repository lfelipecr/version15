from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cabys_id = fields.Many2one(
        string="CAByS",
        comodel_name="cabys",
        ondelete="restrict",
    )
    # taxes_id = fields.Many2many(  # Overwrite base
    #     compute="_compute_tax_from_cabys",
    #     store=True,
    # )
    # taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id',
    #                             help="Default taxes used when selling the product.", string='Impuesto de clientes',
    #                             domain=[('type_tax_use', '=', 'sale')],
    #                             default=lambda self: self.env.company.account_sale_tax_id)

    tax_cabys = fields.Many2one('account.tax', string='Impuesto cabys',compute="_compute_tax_from_cabys",store=True)

    code_cabys = fields.Char(related='cabys_id.code',string='CABYS CODE',store=True)

    @api.depends('cabys_id','cabys_id.tax_id','cabys_id.taxes_ids')
    def _compute_tax_from_cabys(self):  # TODO the change doesn't occur in real time in the frontend

        company_id = self.env.company

        for template in self:
            if not template.cabys_id:
                continue
            #template.tax_cabys = template.cabys_id.tax_id[0]
            # if template.tax_cabys:
            #     template.taxes_id = [(6, None, [template.cabys_id.tax_id.id])]


            #Todo: Cabys para multicompañia

            if company_id:
                cab = template.cabys_id
                for t in cab.taxes_ids:
                    if t.company_id == company_id:
                        template.tax_cabys = t.id
                        if t.type_tax_use == 'sale':
                            #template.taxes_id = [(4, t.id)]
                            template.taxes_id = [(6, None, [t.id])]
                        elif t.type_tax_use == 'purchase':
                            #template.supplier_taxes_id = [(4, t.id)]
                            template.supplier_taxes_id = [(6, None, [t.id])]

                        break



    @api.onchange('cabys_id')
    def _onchange_cabys_id(self):
        self._compute_tax_from_cabys()
