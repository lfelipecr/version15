# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import date, datetime,timedelta,timezone
from io import BytesIO
import base64
from datetime import datetime
import xlsxwriter
from ..utils.excel import header, base_by_activity, tax_by_company

STATE_ODOO = [
    ('draft', 'Borrador'),
    ('posted', 'Publicado'),
    ('cancel', 'Cancelado'),
]

STATE_HACIENDA = [
    ("aceptado", _("Aceptado")),
    ("rechazado", _("Rechazado")),
    ("recibido", _("Recibido")),
    ("error", "Error"),
    ("na", _("No aplica")),
    ("ne", _("No encontrado")),
    ("firma_invalida", _("Firma inválida")),
    ("procesando", _("Procesando")),
]

TYPE_SALE_PRUCHASE =[
    ("all", 'Todas'),
    ("other", _("Bien")),
    ("service", _("Servicio")),
]

MESES = [
    ('1','Enero'),
    ('2','Febrero'),
    ('3','Marzo'),
    ('4','Abril'),
    ('5','Mayo'),
    ('6','Junio'),
    ('7','Julio'),
    ('8','Agosto'),
    ('9','Setiembre'),
    ('10','Octubre'),
    ('11','Noviembre'),
    ('12','Diciembre'),
]

SALE_PURCHASE_TRANSACTION = [
    ("all", 'Todas'),
    ('national','Nacional'),
    ('international','Internacional')
]

class AccountReportIva(models.TransientModel):
    _name = 'account.report.iva.wizard'
    _description = 'Reporte IVA'


    company_id = fields.Many2one('res.company', string=u"Compañia", default=lambda self: self.env.company)


    def _default_journal_ids(self):
        company_id = False
        if self.env.company:
            company_id = self.env.company.id
        return self.env['account.journal'].sudo().search([('to_process','=',True),('company_id','=',company_id)])

    journal_ids = fields.Many2many('account.journal',string='Diarios', default=_default_journal_ids)

    state_odoo = fields.Selection(selection=STATE_ODOO, string='Estado Odoo', default='posted')

    state_hacienda = fields.Selection(selection=STATE_HACIENDA,string='Estado Hacienda',default='aceptado')

    type_date = fields.Selection(selection=[('range','Rango'),('month','Mes')], default='month')

    def _default_month(self):
        mes_actual = date.today().month
        mes_select = mes_actual - 1 #Un mes anterior
        return str(mes_select)

    def _default_year(self):
        return str(date.today().year)

    selected_month = fields.Selection(selection=MESES, default=_default_month, string='Mes')
    selected_year = fields.Char(string='Año', default=_default_year, store=True)

    selected_range_from = fields.Date(string='Fecha inicio')
    selected_range_to = fields.Date(string='Fecha fin')

    #type_activity = fields.Selection(selection=[('all','Todas'),('selected','Personalizado')], default='all')

    def _default_activity_economic(self):
        return self.env.company.activity_ids

    activity_ids = fields.Many2many('economic_activity',string='Actividad Económica', default=_default_activity_economic)

    purchase_type = fields.Selection(selection=TYPE_SALE_PRUCHASE, default='all', string='Tipo Compra')

    purchase_national = fields.Selection(selection=SALE_PURCHASE_TRANSACTION,string='Tipo Transacción Compra',default='all')

    sale_type = fields.Selection(selection=TYPE_SALE_PRUCHASE, default='all', string='Tipo Venta')

    def _default_purchase_taxes(self):
        company_id = False
        if self.env.company:
            company_id = self.env.company.id

        domain = [('type_tax_use', '=', 'purchase'), ('company_id', '=', company_id),
                  '|', ('classification_type', 'in', ['none', 'exempt', 'no_hold', 'exonerated']), ('amount', 'in', (1, 2, 4, 8, 13))]
        return self.env['account.tax'].sudo().search(domain)

    purchase_tax_ids = fields.Many2many('account.tax', 'report_iva_wizar_purchase_tax_rel','report_iva_id','tax_id',
                                        string='Impuestos', default=_default_purchase_taxes) #Tipo de impuesto

    purchase_iva_condition = fields.Selection([('all','Ambos'),('acreditable','Acreditable'),('not_acreditable','No Acreditable')],
                                              default='all')

    sale_iva_condition = fields.Selection([('acreditable','Acreditable')],default='acreditable')


    sale_national = fields.Selection(selection=SALE_PURCHASE_TRANSACTION, default='all', string='Tipo Transacción Venta')

    xls_filename = fields.Char(u'Nombre de fichero')
    xls_file = fields.Binary(u'Descargar reporte', readonly=True)

    def _default_sale_taxes(self):
        company_id = False
        if self.env.company:
            company_id = self.env.company.id
        domain = [('type_tax_use','=','sale'),('company_id', '=', company_id),
                  '|',('classification_type','in',['none','exempt','no_hold','exonerated']),('amount','in',(1,2,4,8,13))]

        return self.env['account.tax'].sudo().search(domain)

    sale_tax_ids = fields.Many2many('account.tax','report_iva_wizar_sale_tax_rel','report_iva_id','tax_id',
                                    string='Impuestos.', default=_default_sale_taxes) #Tipo de impuesto

    xls_filename = fields.Char(u'Nombre de fichero')
    xls_file = fields.Binary(u'Descargar reporte', readonly=True)

    @api.onchange('purchase_iva_condition')
    def _onchange_purchase_iva_condition(self):
        if self.purchase_iva_condition:
            if self.purchase_iva_condition == 'acreditable':
                self.sale_iva_condition = 'acreditable'
            else:
                self.sale_iva_condition = False

    #Generar excel
    def process(self):
        excel = BytesIO()
        workbook = xlsxwriter.Workbook(excel, {'in_memory': True})

        head, header_detalle, body, name, number = header._get_styles(workbook)

        sheet_A = workbook.add_worksheet(u'BASES')
        sheet_A.merge_range('A1:I1', u'Bases disponibles por actividad económica', head)

        sheet_B = workbook.add_worksheet(u'IMPUESTOS')
        sheet_B.merge_range('A1:J1', u'Impuesto en compra y venta', head)

        init = 2
        for activity in self.activity_ids:
            init = base_by_activity._structure_table(self, sheet_A, activity,  init, header_detalle, body, name, number)  #generando tablas
            init += 1

        tbl_init = 2
        tbl_i = [{'tbl':'vnt','name':'VENTAS'},{'tbl':'com','name':'COMPRAS'}] #Donde vnt:Ventas y cmp:Compras
        for t in tbl_i:
            tbl_init = tax_by_company._structure_table(self, sheet_B, activity,  tbl_init, header_detalle, body, name, number, t, workbook) #generando tablas
            tbl_init += 1



        workbook.close()
        excel.seek(0)
        return excel.getvalue()

    def excel_report(self):
        for rpt in self:
            name = datetime.now().strftime("%Y%m%d%H%M%S")
            rpt.write(dict(
                xls_filename='R-IVA' + name + '.xlsx',
                xls_file=base64.b64encode(self.process()),
            ))
            return {
                u'name': u'Reporte IVA',
                u'type': u'ir.actions.act_window',
                u'view_type': u'form',
                u'view_mode': u'form',
                u'target': u'new',
                u'res_model': u'account.report.iva.wizard',
                u'res_id': rpt.id
            }



