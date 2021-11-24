
def _get_styles(workbook):

    header = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 10,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#1F497D',
        'font_color': 'white',
        'border': 0
    })

    name = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#DCE6F1',
        'font_color': '#003a92',
        'border': 0,
        'bold': 1
    })


    header_detalle = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 9,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#efefef',
        'border': 0
    })



    body = workbook.add_format({
        'font_name': 'DejaVu Sans',
        'font_size': 8,
        'align': 'left',
        'valign': 'vcenter',
        'bg_color': '#ffffff',
        'font_color': '#003a92',
        'border': 0
    })


    number = workbook.add_format({'font_name': 'DejaVu Sans',
                                  'font_size': 8,
                                  'align': 'right',
                                  'valign': 'vcenter',
                                  'bg_color': '#ffffff',
                                  'font_color': '#003a92',
                                  'border': 0,
                                  'num_format': '#,###,##0.00'})

    return header, header_detalle, body, name, number
