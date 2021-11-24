from . import base_by_activity_data

def _structure_table(self, sheet, activity,  init, header_detalle, body, name, number):

    #Ancho de las columnas
    sheet.set_column('A:A', 25)
    sheet.set_column('B:B', 13)
    sheet.set_column('C:C', 13)
    sheet.set_column('D:D', 13)
    sheet.set_column('E:E', 13)
    sheet.set_column('F:F', 13)
    sheet.set_column('G:G', 13)
    sheet.set_column('H:H', 13)
    sheet.set_column('I:I', 13)

    data = base_by_activity_data._data(self, activity,)  # generando data de las tablas

    sheet.write(init, 0,u'ACTIVIDAD ECONÓMICA:', name)
    sheet.merge_range('B'+str(init+1)+':I'+str(init+1), activity.name, name)

    init += 1

    #PARTE 1
    sheet.write(init, 0, 'VENTAS NACIONALES', header_detalle)
    sheet.write(init, 1, 'AL 1%', header_detalle)
    sheet.write(init, 2, 'AL 2%', header_detalle)
    sheet.write(init, 3, 'AL 4%', header_detalle)
    sheet.write(init, 4, 'AL 8%', header_detalle)
    sheet.write(init, 5, 'AL 13%', header_detalle)
    sheet.write(init, 6, 'EXENTAS', header_detalle)
    sheet.write(init, 7, 'NO SUJETAS', header_detalle)
    sheet.write(init, 8, 'EXONERADOS', header_detalle)
    init +=1
    sheet.write(init, 0, 'BIENES', header_detalle)
    sheet.write(init, 1, data['vnt_na_bienes']['amount_1'], number)
    sheet.write(init, 2, data['vnt_na_bienes']['amount_2'], number)
    sheet.write(init, 3, data['vnt_na_bienes']['amount_4'], number)
    sheet.write(init, 4, data['vnt_na_bienes']['amount_8'], number)
    sheet.write(init, 5, data['vnt_na_bienes']['amount_13'], number)
    sheet.write(init, 6, data['vnt_na_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data['vnt_na_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data['vnt_na_bienes']['amount_exonerated'], number)

    init += 1
    sheet.write(init, 0, 'SERVICIOS', header_detalle)
    sheet.write(init, 1, data['vnt_na_servicios']['amount_1'], number)
    sheet.write(init, 2, data['vnt_na_servicios']['amount_2'],number)
    sheet.write(init, 3, data['vnt_na_servicios']['amount_4'], number)
    sheet.write(init, 4, data['vnt_na_servicios']['amount_8'], number)
    sheet.write(init, 5, data['vnt_na_servicios']['amount_13'], number)
    sheet.write(init, 6, data['vnt_na_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data['vnt_na_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data['vnt_na_servicios']['amount_exonerated'], number)

    # PARTE 2
    init += 2
    sheet.write(init, 0, 'VENTAS AL EXTERIOR', header_detalle)
    sheet.write(init, 1, 'AL 1%', header_detalle)
    sheet.write(init, 2, 'AL 2%', header_detalle)
    sheet.write(init, 3, 'AL 4%', header_detalle)
    sheet.write(init, 4, 'AL 8%', header_detalle)
    sheet.write(init, 5, 'AL 13%', header_detalle)
    sheet.write(init, 6, 'EXENTAS', header_detalle)
    sheet.write(init, 7, 'NO SUJETAS', header_detalle)
    sheet.write(init, 8, 'EXONERADOS', header_detalle)
    init += 1
    sheet.write(init, 0, 'BIENES', header_detalle)
    sheet.write(init, 1, data['vnt_ex_bienes']['amount_1'], number)
    sheet.write(init, 2, data['vnt_ex_bienes']['amount_2'], number)
    sheet.write(init, 3, data['vnt_ex_bienes']['amount_4'], number)
    sheet.write(init, 4, data['vnt_ex_bienes']['amount_8'], number)
    sheet.write(init, 5, data['vnt_ex_bienes']['amount_13'], number)
    sheet.write(init, 6, data['vnt_ex_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data['vnt_ex_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data['vnt_ex_bienes']['amount_exonerated'], number)
    init += 1
    sheet.write(init, 0, 'SERVICIOS', header_detalle)
    sheet.write(init, 1, data['vnt_ex_servicios']['amount_1'], number)
    sheet.write(init, 2, data['vnt_ex_servicios']['amount_2'], number)
    sheet.write(init, 3, data['vnt_ex_servicios']['amount_4'], number)
    sheet.write(init, 4, data['vnt_ex_servicios']['amount_8'], number)
    sheet.write(init, 5, data['vnt_ex_servicios']['amount_13'], number)
    sheet.write(init, 6, data['vnt_ex_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data['vnt_ex_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data['vnt_ex_servicios']['amount_exonerated'], number)

    # PARTE 3

    # Parte 3.1
    init += 2
    sheet.write(init, 0, 'IVA ACREDITABLE', header_detalle)
    init +=1
    sheet.write(init, 0, 'COMPRAS NACIONALES', header_detalle)
    sheet.write(init, 1, 'AL 1%', header_detalle)
    sheet.write(init, 2, 'AL 2%', header_detalle)
    sheet.write(init, 3, 'AL 4%', header_detalle)
    sheet.write(init, 4, 'AL 8%', header_detalle)
    sheet.write(init, 5, 'AL 13%', header_detalle)
    sheet.write(init, 6, 'EXENTAS', header_detalle)
    sheet.write(init, 7, 'NO SUJETAS', header_detalle)
    sheet.write(init, 8, 'EXONERADOS', header_detalle)
    init += 1
    sheet.write(init, 0, 'BIENES', header_detalle)
    sheet.write(init, 1, data['com_iva_ac_na_bienes']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_ac_na_bienes']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_ac_na_bienes']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_ac_na_bienes']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_ac_na_bienes']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_ac_na_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_ac_na_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_ac_na_bienes']['amount_exonerated'], number)
    init += 1
    sheet.write(init, 0, 'SERVICIOS', header_detalle)
    sheet.write(init, 1, data['com_iva_ac_na_servicios']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_ac_na_servicios']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_ac_na_servicios']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_ac_na_servicios']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_ac_na_servicios']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_ac_na_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_ac_na_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_ac_na_servicios']['amount_exonerated'], number)

    init += 2 #Separacion
    # Parte 3.2
    sheet.write(init, 0, 'COMPRAS AL EXTERIOR', header_detalle)
    sheet.write(init, 1, 'AL 1%', header_detalle)
    sheet.write(init, 2, 'AL 2%', header_detalle)
    sheet.write(init, 3, 'AL 4%', header_detalle)
    sheet.write(init, 4, 'AL 8%', header_detalle)
    sheet.write(init, 5, 'AL 13%', header_detalle)
    sheet.write(init, 6, 'EXENTAS', header_detalle)
    sheet.write(init, 7, 'NO SUJETAS', header_detalle)
    sheet.write(init, 8, 'EXONERADOS', header_detalle)
    init += 1
    sheet.write(init, 0, 'BIENES', header_detalle)
    sheet.write(init, 1, data['com_iva_ac_ex_bienes']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_ac_ex_bienes']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_ac_ex_bienes']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_ac_ex_bienes']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_ac_ex_bienes']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_ac_ex_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_ac_ex_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_ac_ex_bienes']['amount_exonerated'], number)

    init += 1
    sheet.write(init, 0, 'SERVICIOS', header_detalle)
    sheet.write(init, 1, data['com_iva_ac_ex_servicios']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_ac_ex_servicios']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_ac_ex_servicios']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_ac_ex_servicios']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_ac_ex_servicios']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_ac_ex_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_ac_ex_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_ac_ex_servicios']['amount_exonerated'], number)

    # PARTE 4
    init += 2
    sheet.write(init, 0, 'SIN IVA O NO ACREDITABLE', header_detalle)
    init += 1
    sheet.write(init, 0, 'COMPRAS NACIONALES', header_detalle)
    sheet.write(init, 1, 'AL 1%', header_detalle)
    sheet.write(init, 2, 'AL 2%', header_detalle)
    sheet.write(init, 3, 'AL 4%', header_detalle)
    sheet.write(init, 4, 'AL 8%', header_detalle)
    sheet.write(init, 5, 'AL 13%', header_detalle)
    sheet.write(init, 6, 'EXENTAS', header_detalle)
    sheet.write(init, 7, 'NO SUJETAS', header_detalle)
    sheet.write(init, 8, 'EXONERADOS', header_detalle)
    init += 1
    sheet.write(init, 0, 'BIENES', header_detalle)
    sheet.write(init, 1, data['com_iva_na_na_bienes']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_na_na_bienes']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_na_na_bienes']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_na_na_bienes']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_na_na_bienes']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_na_na_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_na_na_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_na_na_bienes']['amount_exonerated'], number)
    init += 1
    sheet.write(init, 0, 'SERVICIOS', header_detalle)
    sheet.write(init, 1, data['com_iva_na_na_servicios']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_na_na_servicios']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_na_na_servicios']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_na_na_servicios']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_na_na_servicios']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_na_na_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_na_na_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_na_na_servicios']['amount_exonerated'], number)

    init += 2  # Separacion
    # Parte 3.2
    sheet.write(init, 0, 'COMPRAS AL EXTERIOR', header_detalle)
    sheet.write(init, 1, 'AL 1%', header_detalle)
    sheet.write(init, 2, 'AL 2%', header_detalle)
    sheet.write(init, 3, 'AL 4%', header_detalle)
    sheet.write(init, 4, 'AL 8%', header_detalle)
    sheet.write(init, 5, 'AL 13%', header_detalle)
    sheet.write(init, 6, 'EXENTAS', header_detalle)
    sheet.write(init, 7, 'NO SUJETAS', header_detalle)
    sheet.write(init, 8, 'EXONERADOS', header_detalle)
    init += 1
    sheet.write(init, 0, 'BIENES', header_detalle)
    sheet.write(init, 1, data['com_iva_na_ex_bienes']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_na_ex_bienes']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_na_ex_bienes']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_na_ex_bienes']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_na_ex_bienes']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_na_ex_bienes']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_na_ex_bienes']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_na_ex_bienes']['amount_exonerated'], number)
    init += 1
    sheet.write(init, 0, 'SERVICIOS', header_detalle)
    sheet.write(init, 1, data['com_iva_na_ex_servicios']['amount_1'], number)
    sheet.write(init, 2, data['com_iva_na_ex_servicios']['amount_2'], number)
    sheet.write(init, 3, data['com_iva_na_ex_servicios']['amount_4'], number)
    sheet.write(init, 4, data['com_iva_na_ex_servicios']['amount_8'], number)
    sheet.write(init, 5, data['com_iva_na_ex_servicios']['amount_13'], number)
    sheet.write(init, 6, data['com_iva_na_ex_servicios']['amount_exempt'], number)
    sheet.write(init, 7, data['com_iva_na_ex_servicios']['amount_no_hold'], number)
    sheet.write(init, 8, data['com_iva_na_ex_servicios']['amount_exonerated'], number)

    #Retorno de separacion para la proxima tabla
    init += 3

    return init

