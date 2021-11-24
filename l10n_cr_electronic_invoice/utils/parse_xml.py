import base64
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from lxml import etree, objectify
from email.message import EmailMessage
import json

_logger = logging.getLogger(__name__)

MOVE_INVOICE = {
    'FacturaElectronica': ['FE', 'in_invoice'],
    'NotaCreditoElectronica': ['NC', 'in_refund'],
    'NotaDebitoElectronica': ['ND', 'in_invoice'],
    'TiqueteElectronico': ['TE', 'in_invoice'],
}


def parseXml(self, values, attachments, invoice_import_ids):
    vals = {}
    for att in attachments:
        if att and att.fname[-3:] == "xml":
            rs = data_xml(self, att, invoice_import_ids)
            vals.update(rs)
    return vals


def data_xml(self, att, invoice_import_ids):
    content = att.content
    if isinstance(content, str):
        content = content.encode('utf-8')
    elif isinstance(content, EmailMessage):
        content = content.as_bytes()

    xml_code = base64.b64encode(content)
    xml_string = re.sub(' xmlns="[^"]+"', "", base64.b64decode(xml_code).decode("utf-8"), count=1, ).encode("utf-8")
    root = ET.fromstring(xml_string, parser=etree.XMLParser(encoding='utf-8', remove_blank_text=True))
    xml_decoded = base64.b64decode(xml_code)
    try:
        factura = etree.fromstring(xml_decoded)

    except Exception as e:
        _logger.error("MAB - This XML file is not XML-compliant. Exception {}".format(e))
        return {"status": 400, "text": "Excepción de conversión de XML"}

    # pretty_xml_string = etree.tostring(factura, pretty_print=True, encoding="UTF-8", xml_declaration=True)
    # _logger.info("Send_file XML: {}".format(pretty_xml_string))

    if root.tag in ('FacturaElectronica', 'NotaCreditoElectronica', 'NotaDebitoElectronica'):

        dict_type_document = MOVE_INVOICE[root.tag]

        tipo_documento = dict_type_document[0]
        move_type = dict_type_document[1]
        r = 1
        namespaces = factura.nsmap
        inv_xmlns = namespaces.pop(None)
        namespaces["inv"] = inv_xmlns

        consecutive_number_receiver = factura.xpath("inv:NumeroConsecutivo", namespaces=namespaces)[0].text
        payment_reference = consecutive_number_receiver
        number_electronic = factura.xpath("inv:Clave", namespaces=namespaces)[0].text
        date_issuance = factura.xpath("inv:FechaEmision", namespaces=namespaces)[0].text
        if "." in date_issuance:  # Time with milliseconds
            date_issuance = date_issuance[: date_issuance.find(".") + 7]  # Truncate first 6 digits of seconds
        date_formats = [
            "%Y-%m-%dT%H:%M:%S-06:00",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        for date_format in date_formats:
            try:
                date_time_obj = datetime.strptime(date_issuance, date_format)
                break
            except ValueError:
                continue
        else:
            _logger.error("No valid date format for {}").format(date_issuance)
            r = 0
        invoice_date = date_time_obj.date()

        try:
            emisor = factura.xpath("inv:Emisor/inv:Identificacion/inv:Numero", namespaces=namespaces)[0].text
        except IndexError:
            _logger.error("The issuer has no identification number, the xml received is invalid")
            r = 0

        try:
            receptor = factura.xpath("inv:Receptor/inv:Identificacion/inv:Numero", namespaces=namespaces)[0].text
        except IndexError:
            _logger.error("The receiver has no identification number, the xml received is invalid")
            r = 0

        company = self.env['res.company'].sudo().search([('vat', '=', receptor)])
        if not company:
            _logger.info('No se encontró la compañia')
            r = 0
            return {}

        invoice_import_ids_company = self.env['account.move.import.config'].sudo().search([('active', '=', True), ('company_id', '=', company.id)], limit=1)

        if not invoice_import_ids_company:
            _logger.info('Posiblemente la compañia de la factura no tenga una configuración hecha o no tiene la configuración activa, revise por favor.')
            r = 0
            return {}
        invoice_import_ids = invoice_import_ids_company

        invs = self.env['account.move'].search([('company_id', '=', company.id),
                                                ('number_electronic', '=', number_electronic),
                                                ('number_electronic', '!=', False),
                                                ('move_type', '=', 'in_invoice'),
                                                ])
        if invs:
            _logger.info('La clave de comprobante debe ser única. Puede ser que este comprobante ya esté registrado.')
            return {}

        currency_node = factura.xpath("inv:ResumenFactura/inv:CodigoTipoMoneda/inv:CodigoMoneda", namespaces=namespaces)

        tipo_cambio = factura.xpath("inv:ResumenFactura/inv:CodigoTipoMoneda/inv:TipoCambio", namespaces=namespaces, )
        if currency_node:
            currency_id = self.env["res.currency"].search([("name", "=", currency_node[0].text)], limit=1).id
            rate_currency = self.env['res.currency.rate'].sudo().search([('name', '=', str(date_issuance)),
                                                                         ('company_id', '=', company.id)], limit=1)
            if not rate_currency and tipo_cambio:
                if float(tipo_cambio[0].text) > 1:
                    rate_currency = self.env['res.currency.rate'].sudo().create({'name': invoice_date,
                                                                                 'rate': round((1 / float(tipo_cambio[0].text)), 12),
                                                                                 'currency_id': currency_id,
                                                                                 'company_id': company.id,
                                                                                 })

        else:
            currency_id = self.env["res.currency"].sudo().search([("name", "=", "CRC")], limit=1).id

        partner = self.env["res.partner"].sudo().search([("vat", "=", emisor),
                                                         ("supplier_rank", ">", 0),
                                                         "|",
                                                         ("company_id", "=", company.id),
                                                         ("company_id", "=", False),
                                                         ], limit=1, )

        #plazos de pago
        invoice_payment_term_id = False
        if invoice_import_ids.supplier_plazo_pago:
            invoice_payment_term_id = invoice_import_ids.supplier_plazo_pago

        if partner:
            partner_id = partner.id
        else:
            partner_id = create_partner(self, root, namespaces, company, invoice_payment_term_id)
            # _logger.error("The provider with id {} does not exist. Please create it in the system first.").format(emisor)
            # r = 0

        # EXTRAS:
        condicion_venta_code = factura.xpath("inv:CondicionVenta", namespaces=namespaces)[0].text
        sale_condition = self.env['sale.conditions'].sudo().search([('sequence', '=', condicion_venta_code)], limit=1)
        termino_pago = self.env['account.payment.term'].sudo().search([('sale_conditions_id', '=', sale_condition.id),
                                                                       '|',
                                                                       ('company_id', '=', company.id),
                                                                       ('company_id', '=', False)], limit=1)

        medio_pago_code = factura.xpath("inv:MedioPago", namespaces=namespaces)[0].text
        medio_pago = self.env['payment.methods'].sudo().search([('sequence', '=', medio_pago_code)], limit=1)

        tax_node = factura.xpath("inv:ResumenFactura/inv:TotalImpuesto", namespaces=namespaces)

        amount_tax_electronic_invoice = 0.0
        if tax_node:
            amount_tax_electronic_invoice = tax_node[0].text

        amount_total_electronic_invoice = factura.xpath("inv:ResumenFactura/inv:TotalComprobante", namespaces=namespaces)[0].text

        lines = root.find("DetalleServicio").findall("LineaDetalle")

        account = invoice_import_ids.account_id
        tax_ids = invoice_import_ids.tax_id
        journal_id = invoice_import_ids.journal_id.id
        product_product_id = invoice_import_ids.product_id
        analytic_id = invoice_import_ids.account_analytic_id

        # Tipo de línea en el detalle del comprobante
        line_type = invoice_import_ids.line_type

        payment_method_id = False
        if invoice_import_ids.supplier_metodo_pago:
            payment_method_id = invoice_import_ids.supplier_metodo_pago

        invoice_line_ids = False
        if line_type != 'line_no_create': #Para el caso de que no desee crear líneas en las facturas.
            invoice_line_ids = data_line(self, att, lines, account, tax_ids, line_type, product_product_id, company, analytic_id)
        if line_type == 'line_no_create':
            amount_tax_electronic_invoice = 0.0
            amount_total_electronic_invoice = 0.0

        if r:
            values = {
                'name': '/',
                'tipo_documento': tipo_documento,
                'move_type': move_type,
                'ref': consecutive_number_receiver or False,
                'journal_id': journal_id,
                'consecutive_number_receiver': consecutive_number_receiver,
                # 'payment_reference': payment_reference,
                'number_electronic': number_electronic,
                'date_issuance': date_issuance,
                'invoice_date': date_issuance,
                'date': date_issuance,
                # 'invoice_date': invoice_date,
                'currency_id': currency_id,
                'partner_id': partner_id,
                'invoice_payment_term_id': invoice_payment_term_id.id if invoice_payment_term_id else (termino_pago.id or False),
                'payment_method_id': payment_method_id.id if payment_method_id else (medio_pago.id or False),
                'amount_tax_electronic_invoice': amount_tax_electronic_invoice,
                'amount_total_electronic_invoice': amount_total_electronic_invoice,
                'invoice_line_ids': invoice_line_ids,
                'company_id': company.id,
                'from_mail': True,
                'fname_xml_supplier_approval': att.fname,
                'xml_supplier_approval': xml_code,
                #'invoice_payment_term_id': invoice_payment_term_id,

            }

        else:
            values = {}

        return values
    else:
        return {}


def data_line(self, att, lines, account, tax_ids, line_type, product_product_id, company, analytic_id):
    """Preparando lineas de factura"""

    array_lines = []
    for line in lines:

        product_ide = False
        detalle = line.find("Detalle").text
        codigo = line.find("Codigo").text,

        und_med = line.find("UnidadMedida")
        product_uom = False
        if und_med is not None:
            pu = self.env["uom.uom"].sudo().search([("code", "=", line.find("UnidadMedida").text)], limit=1)
            if pu:
                product_uom = pu.id
        total_amount = float(line.find("MontoTotal").text)
        discount_percentage = 0.0
        discount_note = None
        discount_node = line.find("Descuento")
        if discount_node is not None:
            discount_amount_node = discount_node.find("MontoDescuento")
            discount_amount = float(discount_amount_node.text or "0.0")
            discount_percentage = discount_amount / total_amount * 100
            discount_note = discount_node.find("NaturalezaDescuento").text
        else:
            discount_amount_node = line.find("MontoDescuento")
            if discount_amount_node:
                discount_amount = float(discount_amount_node.text or "0.0")
                discount_percentage = discount_amount / total_amount * 100
                discount_note = line.find("NaturalezaDescuento").text

        total_tax = 0.0
        taxes = self.env["account.tax"]
        tax_nodes = line.findall("Impuesto")

        if tax_nodes is not None:
            for tax_node in tax_nodes:
                if tax_node:
                    tax_amount = float(tax_node.find("Monto").text)
                    codigo_tax = re.sub(r"[^0-9]+", "", tax_node.find("Codigo").text)
                    if codigo_tax is not None:
                        tax = self.env["account.tax"].sudo().search([("tax_code", "=", codigo_tax),
                                                                     ("amount", "=", tax_node.find("Tarifa").text),
                                                                     ("type_tax_use", "=", "purchase"),
                                                                     ('company_id', '=', company.id)
                                                                     ], limit=1, )
                        if tax:
                            taxes += tax
                            total_tax += tax_amount
                        else:
                            _logger.error("A tax type in the XML does not exist in the configuration: {}").format(tax_node.find("Codigo").text)

        # Todo: Evaluamos si creamos o no el producto, dependiendo de la configuración
        tax_supplier_id = False
        if line_type == 'product_create':
            domain_cabys = []
            domain_cabys.append(('code', '=', codigo))
            if tax_nodes:
                codigo_tarifa = tax_nodes[0].find('CodigoTarifa').text
                if codigo_tarifa:
                    tax_supplier_id = self.env["account.tax"].sudo().search([('iva_tax_code', '=', codigo_tarifa), ('company_id', '=', company.id)], limit=1)
                    if tax_supplier_id:
                        domain_cabys.append(('taxes_ids', 'in', tax_supplier_id.id))

            domain_product = []
            domain_product.append(('name', 'like', detalle))

            cabys = self.env['cabys'].sudo().search(domain_cabys, limit=1)
            if cabys:
                domain_product.append(('cabys_id', '=', cabys.id))

            product_find = self.env['product.template'].sudo().search(domain_product, limit=1)
            if not product_find:
                dict_p = {'name': detalle,
                          'purchase_ok': True,
                          'cabys_id': cabys.id if cabys else False,
                          'supplier_taxes_id': False
                          }
                if tax_supplier_id:
                    dict_p['supplier_taxes_id'] = [(4, tax_supplier_id.id)]

                product_find = self.env['product.template'].create(dict_p)

            if not tax_supplier_id and product_find:
                product_find.write({'supplier_taxes_id': []})

            product_ide = product_find.product_variant_id.id
        elif line_type == 'product_no_create':
            pass
        elif line_type == 'product_default':
            product_ide = product_product_id.id if product_product_id else False
        else:
            pass

        account_id = account.id

        def _create_dict(line):

            def _create_tax(line):

                tax_array = []
                tax_nodes = line.findall("Impuesto")
                if tax_nodes:
                    for tax_node in tax_nodes:
                        js_tax = {
                            'codigo': re.sub(r"[^0-9]+", "", tax_node.find("Codigo").text),
                            'codigo_tarifa': re.sub(r"[^0-9]+", "", tax_node.find("CodigoTarifa").text),
                            'tarifa': tax_node.find("Tarifa").text,
                            'monto': tax_node.find("Monto").text,
                        }
                        tax_array.append(js_tax)

                return tax_array

            if line.find('ImpuestoNeto') is None:
                impuesto_neto = 0.0
            else:
                impuesto_neto = line.find('ImpuestoNeto').text

            js = {
                'num_linea': line.find('NumeroLinea').text,
                'codigo': line.find('Codigo').text,
                'cantidad': line.find('Cantidad').text,
                'unidad_medida': line.find('UnidadMedida').text,
                'detalle': line.find('Detalle').text,
                'precio_unitario': line.find('PrecioUnitario').text,
                'monto_total': line.find('MontoTotal').text,
                'sub_total': line.find('SubTotal').text,
                'impuesto': _create_tax(line),
                'impuesto_neto': impuesto_neto,
                'monto_total_linea': line.find('MontoTotalLinea').text,
            }

            return js

        data = {
            # 'sequence': line.find("NumeroLinea").text,
            'name': line.find("Detalle").text,
            'product_id': product_ide,
            'price_unit': line.find("PrecioUnitario").text,
            'quantity': line.find("Cantidad").text,
            'product_uom_id': product_uom,
            'discount': discount_percentage,
            'discount_note': discount_note,
            'tax_ids': taxes,
            'total_tax': total_tax,
            'account_id': account_id,
            'analytic_account_id': analytic_id.id if analytic_id else False,
            'info_json': json.dumps(_create_dict(line))
        }
        array_lines.append((0, 0, data))

    return array_lines


def create_partner(self, root, namespaces, company, invoice_payment_term_id):
    emisor = root.find("Emisor")
    commercial_name_tag = root.find("Emisor").find("NombreComercial")
    email_tag = root.find("Emisor").find("CorreoElectronico")
    ubicacion = root.find("Emisor").find("Ubicacion")
    telefono = root.find("Emisor").find("Telefono")

    name = emisor.find('Nombre').text
    type_code = emisor.find('Identificacion').find('Tipo').text
    vat = emisor.find('Identificacion').find('Numero').text

    provincia_code = None
    canton_code = None
    distrito_code = None
    barrio_code = None
    street_tag = None

    if ubicacion is not None:
        provincia_code = ubicacion.find('Provincia')
        canton_code = ubicacion.find('Canton')
        distrito_code = ubicacion.find('Distrito')
        barrio_code = ubicacion.find('Barrio')
        street_tag = ubicacion.find('OtrasSenas')

    commercial_name = False
    if commercial_name_tag is not None:
        commercial_name = commercial_name_tag.text

    email = False
    if email_tag is not None:
        email = email_tag.text

    provincia = False
    canton = False
    distrito = False
    barrio = False

    code_pais = None
    telefono_code = None
    if telefono is not None:
        code_pais = telefono.find('CodigoPais')
        telefono_code = telefono.find('NumTelefono')

    pais_id = company.country_id.id
    if type_code is not None:
        type_id = self.env['identification.type'].sudo().search([('code', '=', type_code)], limit=1)
    if provincia_code is not None:
        provincia = self.env['res.country.state'].sudo().search([('code', '=', provincia_code.text), ('country_id', '=', pais_id)], limit=1)
        if provincia and (canton_code is not None):
            canton = self.env['res.country.county'].sudo().search([('code', '=', canton_code.text), ('state_id', '=', provincia.id)], limit=1)
            if canton and (distrito_code is not None):
                distrito = self.env['res.country.district'].sudo().search([('code', '=', distrito_code.text), ('county_id', '=', canton.id)], limit=1)
                if distrito and (barrio_code is not None):
                    barrio = self.env['res.country.neighborhood'].sudo().search([('code', '=', barrio_code.text), ('district_id', '=', distrito.id)], limit=1)
    phone = False
    mobile = False
    if (code_pais is not None) and (telefono_code is not None):
        phone = code_pais.text + ' ' + telefono_code.text
        mobile = code_pais.text + ' ' + telefono_code.text

    street = False
    if street_tag is not None:
        street = street_tag.text

    property_supplier_payment_term_id = False
    if invoice_payment_term_id:
        property_supplier_payment_term_id = invoice_payment_term_id.id

    partner_vals = {
        'type': False,
        'name': name,
        'identification_id': type_id.id,
        'vat': vat,
        'country_id': pais_id,
        'state_id': provincia.id if provincia else False,
        'county_id': canton.id if canton else False,
        'district_id': distrito.id if distrito else False,
        'neighborhood_id': barrio.id if barrio else False,
        'phone': phone,
        'mobile': mobile,
        'street': street,
        'email': email,
        'commercial_name': commercial_name,
        'supplier_rank': 999,
        'property_supplier_payment_term_id': property_supplier_payment_term_id,
    }

    partner = self.env['res.partner'].sudo().create(partner_vals)
    return partner.id
