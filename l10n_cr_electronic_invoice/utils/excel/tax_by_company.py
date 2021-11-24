from . import tax_by_company_data

def _structure_table(self, sheet, activity,  init, header_detalle, body, name, number, tbl, workbook):


    detalle_negrita = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 9,
        'align': 'left',
        'valign': 'vcenter',
        'bg_color': '#efefef',
        'border': 0,
        'bold': 1
    })

    sub_header = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 9,
        'align': 'right',
        'valign': 'vcenter',
        'bg_color': '#efefef',
        'border': 0,
        'num_format': '#,###,##0.00'
    })

    header_detalle_sub = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 8,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#efefef',
        'border': 0
    })

    name_sub = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#efefef',
        'border': 0,
        'font_color': '#00B050',
    })

    #Ancho de las columnas
    sheet.set_column('A:A', 15)
    sheet.set_column('B:B', 13)
    sheet.set_column('C:C', 13)
    sheet.set_column('D:D', 13)
    sheet.set_column('E:E', 13)
    sheet.set_column('F:F', 13)
    sheet.set_column('G:G', 13)
    sheet.set_column('H:H', 13)
    sheet.set_column('I:I', 13)
    sheet.set_column('J:J', 13)

    data = tax_by_company_data._data(self)  # generando data de las tablas

    sheet.merge_range('A'+str(init)+':J'+str(init), tbl['name'], name)

    init += 2

    detalle = header_detalle
    #PARTE 1
    sheet.write(init, 0, 'DETALLE', detalle_negrita)
    sheet.write(init, 1, 'AL 1%', detalle_negrita)
    sheet.write(init, 2, 'AL 2%', detalle_negrita)
    sheet.write(init, 3, 'AL 4%', detalle_negrita)
    sheet.write(init, 4, 'AL 8%', detalle_negrita)
    sheet.write(init, 5, 'AL 13%', detalle_negrita)
    sheet.write(init, 6, 'EXENTAS', detalle_negrita)
    sheet.write(init, 7, 'NO SUJETAS', detalle_negrita)
    sheet.write(init, 8, 'EXONERADOS', detalle_negrita)
    sheet.write(init, 9, 'TOTAL', detalle_negrita)
    init +=1
    sheet.write(init, 0, 'BIENES', name_sub)
    sheet.write(init, 1,  data[tbl['tbl']+'_na_bienes']['amount_1'] +  data[tbl['tbl']+'_ex_bienes']['amount_1'], sub_header)
    sheet.write(init, 2,  data[tbl['tbl']+'_na_bienes']['amount_2'] +  data[tbl['tbl']+'_ex_bienes']['amount_2'], sub_header)
    sheet.write(init, 3,  data[tbl['tbl']+'_na_bienes']['amount_4'] +  data[tbl['tbl']+'_ex_bienes']['amount_4'], sub_header)
    sheet.write(init, 4,  data[tbl['tbl']+'_na_bienes']['amount_8'] +  data[tbl['tbl']+'_ex_bienes']['amount_8'], sub_header)
    sheet.write(init, 5,  data[tbl['tbl']+'_na_bienes']['amount_13'] +  data[tbl['tbl']+'_ex_bienes']['amount_13'], sub_header)
    sheet.write(init, 6,  data[tbl['tbl']+'_na_bienes']['amount_exempt'] +  data[tbl['tbl']+'_ex_bienes']['amount_exempt'], sub_header)
    sheet.write(init, 7,  data[tbl['tbl']+'_na_bienes']['amount_no_hold'] +  data[tbl['tbl']+'_ex_bienes']['amount_no_hold'], sub_header)
    sheet.write(init, 8,  data[tbl['tbl']+'_na_bienes']['amount_exonerated'] +  data[tbl['tbl']+'_ex_bienes']['amount_exonerated'], sub_header)
    sheet.write(init, 9,  data[tbl['tbl']+'_na_bienes']['total'] +  data[tbl['tbl']+'_ex_bienes']['total'], sub_header)

    init += 1

    sheet.write(init, 0, 'LOCALES', header_detalle_sub)
    sheet.write(init, 1, data[tbl['tbl']+'_na_bienes']['amount_1'], number)
    sheet.write(init, 2, data[tbl['tbl']+'_na_bienes']['amount_2'], number)
    sheet.write(init, 3, data[tbl['tbl']+'_na_bienes']['amount_4'], number)
    sheet.write(init, 4, data[tbl['tbl']+'_na_bienes']['amount_8'], number)
    sheet.write(init, 5, data[tbl['tbl']+'_na_bienes']['amount_13'], number)
    sheet.write(init, 6, data[tbl['tbl']+'_na_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data[tbl['tbl']+'_na_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data[tbl['tbl']+'_na_bienes']['amount_exonerated'], number)
    sheet.write(init, 9, data[tbl['tbl']+'_na_bienes']['total'], number)

    init += 1

    sheet.write(init, 0, 'IMPORTADOS', header_detalle_sub)
    sheet.write(init, 1, data[tbl['tbl']+'_ex_bienes']['amount_1'], number)
    sheet.write(init, 2, data[tbl['tbl']+'_ex_bienes']['amount_2'],number)
    sheet.write(init, 3, data[tbl['tbl']+'_ex_bienes']['amount_4'], number)
    sheet.write(init, 4, data[tbl['tbl']+'_ex_bienes']['amount_8'], number)
    sheet.write(init, 5, data[tbl['tbl']+'_ex_bienes']['amount_13'], number)
    sheet.write(init, 6, data[tbl['tbl']+'_ex_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data[tbl['tbl']+'_ex_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data[tbl['tbl']+'_ex_bienes']['amount_exonerated'], number)
    sheet.write(init, 9, data[tbl['tbl']+'_ex_bienes']['total'], number)

    init += 1

    sheet.write(init, 0, 'SERVICIOS', name_sub)
    sheet.write(init, 1,  data[tbl['tbl']+'_na_servicios']['amount_1'] +  data[tbl['tbl']+'_ex_servicios']['amount_1'], sub_header)
    sheet.write(init, 2,  data[tbl['tbl']+'_na_servicios']['amount_2'] +  data[tbl['tbl']+'_ex_servicios']['amount_2'], sub_header)
    sheet.write(init, 3,  data[tbl['tbl']+'_na_servicios']['amount_4'] +  data[tbl['tbl']+'_ex_servicios']['amount_4'], sub_header)
    sheet.write(init, 4,  data[tbl['tbl']+'_na_servicios']['amount_8'] +  data[tbl['tbl']+'_ex_servicios']['amount_8'], sub_header)
    sheet.write(init, 5,  data[tbl['tbl']+'_na_servicios']['amount_13'] +  data[tbl['tbl']+'_ex_servicios']['amount_13'], sub_header)
    sheet.write(init, 6,  data[tbl['tbl']+'_na_servicios']['amount_exempt'] +  data[tbl['tbl']+'_ex_servicios']['amount_exempt'], sub_header)
    sheet.write(init, 7,  data[tbl['tbl']+'_na_servicios']['amount_no_hold'] +  data[tbl['tbl']+'_ex_servicios']['amount_no_hold'], sub_header)
    sheet.write(init, 8,  data[tbl['tbl']+'_na_servicios']['amount_exonerated'] +  data[tbl['tbl']+'_ex_servicios']['amount_exonerated'], sub_header)
    sheet.write(init, 9,  data[tbl['tbl']+'_na_servicios']['total'] +  data[tbl['tbl']+'_ex_servicios']['total'], sub_header)

    init += 1

    sheet.write(init, 0, 'LOCALES', header_detalle_sub)
    sheet.write(init, 1, data[tbl['tbl']+'_na_servicios']['amount_1'], number)
    sheet.write(init, 2, data[tbl['tbl']+'_na_servicios']['amount_2'], number)
    sheet.write(init, 3, data[tbl['tbl']+'_na_servicios']['amount_4'], number)
    sheet.write(init, 4, data[tbl['tbl']+'_na_servicios']['amount_8'], number)
    sheet.write(init, 5, data[tbl['tbl']+'_na_servicios']['amount_13'], number)
    sheet.write(init, 6, data[tbl['tbl']+'_na_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data[tbl['tbl']+'_na_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data[tbl['tbl']+'_na_servicios']['amount_exonerated'], number)
    sheet.write(init, 9, data[tbl['tbl']+'_na_servicios']['total'], number)

    init += 1
    sheet.write(init, 0, 'IMPORTADOS', header_detalle_sub)
    sheet.write(init, 1, data[tbl['tbl']+'_ex_servicios']['amount_1'], number)
    sheet.write(init, 2, data[tbl['tbl']+'_ex_servicios']['amount_2'], number)
    sheet.write(init, 3, data[tbl['tbl']+'_ex_servicios']['amount_4'], number)
    sheet.write(init, 4, data[tbl['tbl']+'_ex_servicios']['amount_8'], number)
    sheet.write(init, 5, data[tbl['tbl']+'_ex_servicios']['amount_13'], number)
    sheet.write(init, 6, data[tbl['tbl']+'_ex_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data[tbl['tbl']+'_ex_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data[tbl['tbl']+'_ex_servicios']['amount_exonerated'], number)
    sheet.write(init, 9, data[tbl['tbl']+'_ex_servicios']['total'], number)

    # Retorno de separacion para la proxima tabla
    init += 3

    return init

