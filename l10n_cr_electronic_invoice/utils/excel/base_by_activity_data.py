from datetime import datetime, date
import calendar
amounts = [1,2,4,8,13]
classification_type = ['exempt','no_hold','exonerated']


CONDICION_IVA = {
    'acreditable': ['gecr','crpa','bica','prop'],
    'not_acreditable': ['gcnc',False],
    'all':  ['gecr','crpa','bica','prop','gcnc',False],
}

def _get_dates(mes):
    mes = int(mes)
    monthRange = calendar.monthrange(datetime.now().year, mes)
    i = date(datetime.now().year, mes, 1)
    f = date(datetime.now().year, mes, monthRange[1])
    return i, f



def _data(self,activity):
    self_move = self.env['account.move'].sudo()
    if self.type_date == 'month':
        fecha_inicio, fecha_fin = _get_dates(self.selected_month)
    else:
        fecha_inicio, fecha_fin = self.selected_range_from, self.selected_range_to

    domain = [
        ('company_id', '=', self.company_id.id),
        ('journal_id', 'in', self.journal_ids.ids),
        ('activity_id','=',activity.id),
        ('state', '=', self.state_odoo),
        '|',('state_tributacion', '=', self.state_hacienda),('state_send_invoice','=',self.state_hacienda),
        ('date','>=', fecha_inicio), ('date','<=',fecha_fin),
    ]

    cols = {
        'vnt_na_bienes': {}, #ventas nacionales bienes
        'vnt_na_servicios': {}, #ventas nacionales servicios
        'vnt_ex_bienes': {}, #ventas al exterior bienes
        'vnt_ex_servicios': {}, #ventas al exterior servicios
        'com_iva_ac_na_bienes': {}, #iva acreditable compras nacionales bienes
        'com_iva_ac_na_servicios': {}, #iva acreditable compras nacionales servicios
        'com_iva_ac_ex_bienes': {}, #iva acreditable compras al exterior bienes
        'com_iva_ac_ex_servicios': {}, #iva acreditable compras al exterior servicios
        'com_iva_na_na_bienes': {}, #iva no acreditable compras nacionales bienes
        'com_iva_na_na_servicios': {}, #iva no acreditable compras nacionales servicios
        'com_iva_na_ex_bienes': {}, #iva no acreditable compras al exterior bienes
        'com_iva_na_ex_servicios': {},  #iva no acreditable compras al exterior servicios
    }

    #TODO: ******************************************************************** VENTAS ***********************************************
    sale_domain = domain + [('move_type', 'in', ('out_invoice','out_refund'))]

    #--------- VENTAS NACIONALES -------------
    vnt_na_bienes = False
    vnt_na_servicios = False
    if self.sale_national in ('national','all'):
        sale_domain_national = sale_domain + [('partner_id.country_id.code','=','CR')]
        sales_moves_nacional = self_move.search(sale_domain_national)
        if self.sale_type == 'other':  # Bien
            vnt_na_bienes = sales_moves_nacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
        elif self.sale_type == 'service':
            vnt_na_servicios = sales_moves_nacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
        elif self.sale_type == 'all':
            vnt_na_bienes = sales_moves_nacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
            vnt_na_servicios = sales_moves_nacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
        else:
            pass

    cols['vnt_na_bienes'] = sumatorias(vnt_na_bienes)
    cols['vnt_na_servicios'] = sumatorias(vnt_na_servicios)

    # --------- VENTAS INTERNACIONALES -------------

    vnt_ex_bienes = False
    vnt_ex_servicios = False
    if self.sale_national in ('international','all'):
        sale_domain_inter = sale_domain + [('partner_id.country_id.code', '!=', 'CR')]
        sales_moves_internacional = self_move.search(sale_domain_inter)
        if self.sale_type == 'other':  # Bien
            vnt_ex_bienes = sales_moves_internacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
        elif self.sale_type == 'service':
            vnt_ex_servicios = sales_moves_internacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
        elif self.sale_type == 'all':
            vnt_ex_bienes = sales_moves_internacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
            vnt_ex_servicios = sales_moves_internacional.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
        else:
            pass

    cols['vnt_ex_bienes'] = sumatorias(vnt_ex_bienes)
    cols['vnt_ex_servicios'] = sumatorias(vnt_ex_servicios)


    #TODO: ******************************************************************** COMPRAS ***********************************************


    purchase_domain = domain + [('move_type', 'in', ('in_invoice','in_refund'))]

    # --------- COMPRAS NACIONALES E INTERNACIONALES IVA ACREDITABLE -------------

    com_iva_ac_na_bienes = False
    com_iva_ac_na_servicios = False
    com_iva_ac_ex_bienes = False
    com_iva_ac_ex_servicios = False
    if self.purchase_iva_condition in ('acreditable','all'):
        domain_acreditable = purchase_domain + [('iva_condition','in',CONDICION_IVA[self.purchase_iva_condition])]
        if self.purchase_national in ('national','all'):
            purchase_domain_national_ac = domain_acreditable + [('partner_id.country_id.code', '=', 'CR')]
            purchase_moves_nacional_ac = self_move.search(purchase_domain_national_ac)
            if self.purchase_type == 'other':  # Bien
                com_iva_ac_na_bienes = purchase_moves_nacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
            elif self.purchase_type == 'service':
                com_iva_ac_na_servicios = purchase_moves_nacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            elif self.purchase_type == 'all':
                com_iva_ac_na_bienes = purchase_moves_nacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
                com_iva_ac_na_servicios = purchase_moves_nacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            else:
                pass

        if self.purchase_national in ('international','all'):
            purchase_domain_international_ac = domain_acreditable + [('partner_id.country_id.code', '!=', 'CR')]
            purchase_moves_internacional_ac = self_move.search(purchase_domain_international_ac)
            if self.purchase_type == 'other':  # Bien
                com_iva_ac_ex_bienes = purchase_moves_internacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
            elif self.purchase_type == 'service':
                com_iva_ac_ex_servicios = purchase_moves_internacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            elif self.purchase_type == 'all':
                com_iva_ac_ex_bienes = purchase_moves_internacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
                com_iva_ac_ex_servicios = purchase_moves_internacional_ac.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            else:
                pass


    cols['com_iva_ac_na_bienes'] = sumatorias(com_iva_ac_na_bienes)
    cols['com_iva_ac_na_servicios'] = sumatorias(com_iva_ac_na_servicios)

    cols['com_iva_ac_ex_bienes'] = sumatorias(com_iva_ac_ex_bienes)
    cols['com_iva_ac_ex_servicios'] = sumatorias(com_iva_ac_ex_servicios)


    # --------- COMPRAS NACIONALES E INTERNACIONALES IVA NO ACREDITABLE -------------

    com_iva_na_na_bienes = False
    com_iva_na_na_servicios = False
    com_iva_na_ex_bienes = False
    com_iva_na_ex_servicios = False

    if self.purchase_iva_condition in ('not_acreditable','all'):
        domain_not_acreditable = purchase_domain + [('iva_condition', 'in', CONDICION_IVA[self.purchase_iva_condition])]
        if self.purchase_national == 'national':
            purchase_domain_national_no_a = domain_not_acreditable + [('partner_id.country_id.code', '=', 'CR')]
            purchase_moves_nacional_no_a = self_move.search(purchase_domain_national_no_a)
            if self.purchase_type == 'other':  # Bien
                com_iva_na_na_bienes = purchase_moves_nacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
            elif self.purchase_type == 'service':
                com_iva_na_na_servicios = purchase_moves_nacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            elif self.purchase_type == 'all':
                com_iva_na_na_bienes = purchase_moves_nacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
                com_iva_na_na_servicios = purchase_moves_nacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            else:
                pass

        if self.purchase_national in ('international','all'):
            purchase_domain_international_no_a = domain_not_acreditable + [('partner_id.country_id.code', '!=', 'CR')]
            purchase_moves_internacional_no_a = self_move.search(purchase_domain_international_no_a)
            if self.purchase_type == 'other':  # Bien
                com_iva_na_ex_bienes = purchase_moves_internacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
            elif self.purchase_type == 'service':
                com_iva_na_ex_servicios = purchase_moves_internacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            elif self.purchase_type == 'all':
                com_iva_na_ex_bienes = purchase_moves_internacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type != 'service')
                com_iva_na_ex_servicios = purchase_moves_internacional_no_a.invoice_line_ids.filtered(lambda sb: sb.product_id.type == 'service')
            else:
                pass

    cols['com_iva_na_na_bienes'] = sumatorias(com_iva_na_na_bienes)
    cols['com_iva_na_na_servicios'] = sumatorias(com_iva_na_na_servicios)

    cols['com_iva_na_ex_bienes'] = sumatorias(com_iva_na_ex_bienes)
    cols['com_iva_na_ex_servicios'] = sumatorias(com_iva_na_ex_servicios)

    return cols



def sumatorias(move_lines):
    r_amounts = {
        'amount_1': 0.0,
        'amount_2': 0.0,
        'amount_4': 0.0,
        'amount_8': 0.0,
        'amount_13': 0.0,
        'amount_exempt': 0.0,
        'amount_no_hold': 0.0,
        'amount_exonerated': 0.0,
    }
    if move_lines:
        for li in move_lines:
            move_id = li.move_id
            for line in move_id.line_ids:
                if line.tax_line_id:
                    for tax in line.tax_line_id:
                        if tax.classification_type == 'none':
                            for amount in amounts:
                                if amount == tax.amount:
                                    #r_amounts['amount_' + str(amount)] += line.move_id.amount_untaxed
                                    r_amounts['amount_' + str(amount)] += line.tax_base_amount
                        elif tax.classification_type in classification_type:
                            for cla in classification_type:
                                if cla == tax.classification_type:
                                    #r_amounts['amount_' + str(cla)] += line.move_id.amount_untaxed
                                    r_amounts['amount_' + str(cla)] += line.tax_base_amount

    return r_amounts
