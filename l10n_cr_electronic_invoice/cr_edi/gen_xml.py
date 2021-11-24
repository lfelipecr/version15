# -*- coding: utf-8 -*-
from xml.sax import saxutils
from odoo import _
from odoo.exceptions import UserError
import phonenumbers

from . import utils



class Templates:
    MensajeReceptor = utils.get_template("MensajeReceptor.xml.jinja")
    FacturaElectronica = utils.get_template("FacturaElectronica.xml.jinja")
    FacturaElectronicaCompra = utils.get_template("FacturaElectronicaCompra.xml.jinja")
    FacturaElectronicaExportacion = utils.get_template("FacturaElectronicaExportacion.xml.jinja")
    NotaCreditoElectronica = utils.get_template("NotaCreditoElectronica.xml.jinja")
    NotaDebitoElectronica = utils.get_template("NotaDebitoElectronica.xml.jinja")
    TiqueteElectronico = utils.get_template("TiqueteElectronico.xml.jinja")
    FacturaElectronicaPos = utils.get_template("FacturaElectronicaPos.xml.jinja")
    NotaCreditoElectronicaPos = utils.get_template("NotaCreditoElectronicaPos.xml.jinja")


def mensaje_receptor(
    electronic_number,
    issuer_vat,
    emition_date,
    message_type,
    message,
    receiver_vat,
    receiver_sequence,
    amount_tax=0,
    amount_total=0,
    activity_code=False,
    tax_status=False,
    amount_tax_to_be_credited=False,
    amount_total_expense=False,
):
    template = Templates.MensajeReceptor
    render = template.render(
        activity_code=activity_code,
        amount_tax=amount_tax,
        amount_tax_to_be_credited=amount_tax_to_be_credited,
        amount_total=amount_total,
        amount_total_expense=amount_total_expense,
        electronic_number=electronic_number,
        emition_date=emition_date,
        issuer_vat=issuer_vat,
        message=saxutils.escape(message),
        message_type=message_type,
        receiver_sequence=receiver_sequence,
        receiver_vat=receiver_vat,
        tax_status=tax_status,
    )
    return render


DOCUMENT_TYPE_TO_TEMPLATE = {
    "FE": Templates.FacturaElectronica,
    "FEC": Templates.FacturaElectronicaCompra,
    "FEE": Templates.FacturaElectronicaExportacion,
    "NC": Templates.NotaCreditoElectronica,
    "ND": Templates.NotaDebitoElectronica,
    "TE": Templates.TiqueteElectronico,
    "FEP": Templates.FacturaElectronicaPos, #Caso especial para factura eletrónica desde POS
    "NCP": Templates.NotaCreditoElectronicaPos, #Caso especial para nota de crédito eletrónica desde POS
}

type_template = {
    'FE' : 'FEP',
    'NC' : 'NCP',
    'TE' : 'TE'
}

def validations(document):
    if document.tipo_documento in ('FE','FEC'):
        if not document.partner_id.phone:
            raise UserError(_("El cliente debe tener un número de teléfono."))
        elif not document.partner_id.country_id:
            raise UserError(_("El cliente debe tener un país."))
        elif not document.partner_id.identification_id:
            raise UserError(_("El cliente debe tener un tipo de documento."))
        elif not document.partner_id.vat:
            raise UserError(_("El cliente debe tener un número de documento de identidad."))

        if not document.company_id.phone:
            raise UserError(_("La compañia debe tener un número de teléfono."))
        elif not document.company_id.country_id:
            raise UserError(_("La compañia debe tener un país."))
        elif not document.company_id.state_id:
            raise UserError(_("La compañia debe tener una provincia."))
        elif not document.company_id.county_id:
            raise UserError(_("La compañia debe tener un cantón."))
        elif not document.company_id.district_id:
            raise UserError(_("La compañia debe tener un distrito."))
        elif not document.company_id.neighborhood_id:
            raise UserError(_("La compañia debe tener un barrio."))
        elif not document.company_id.email:
            raise UserError(_("La compañia debe tener un email."))
        elif not document.company_id.identification_id:
            raise UserError(_("La compañia debe tener un tipo de documento."))
        elif not document.company_id.vat:
            raise UserError(_("La compañia debe tener un número de documento de identidad."))

    elif document.tipo_documento in ('FEE'):

        if not document.company_id.phone:
            raise UserError(_("La compañia debe tener un número de teléfono."))
        elif not document.company_id.country_id:
            raise UserError(_("La compañia debe tener un país."))
        elif not document.company_id.state_id:
            raise UserError(_("La compañia debe tener una provincia."))
        elif not document.company_id.county_id:
            raise UserError(_("La compañia debe tener un cantón."))
        elif not document.company_id.district_id:
            raise UserError(_("La compañia debe tener un distrito."))
        elif not document.company_id.neighborhood_id:
            raise UserError(_("La compañia debe tener un barrio."))
        elif not document.company_id.email:
            raise UserError(_("La compañia debe tener un email."))
        elif not document.company_id.identification_id:
            raise UserError(_("La compañia debe tener un tipo de documento."))
        elif not document.company_id.vat:
            raise UserError(_("La compañia debe tener un número de documento de identidad."))


    elif document.tipo_documento == 'TE':

        """EN TIQUETE ELECTRÓNICO NO ES NECESARIO VALIDAR LOS DATOS DEL CLIENTE"""
        # if not document.partner_id.phone:
        #     raise UserError(_("El cliente debe tener un número de teléfono."))
        # elif not document.partner_id.country_id:
        #     raise UserError(_("El cliente debe tener un país."))
        # elif not document.partner_id.identification_id:
        #     raise UserError(_("El cliente debe tener un tipo de documento."))
        # elif not document.partner_id.vat:
        #     raise UserError(_("El cliente debe tener un número de documento de identidad."))

        if not document.company_id.phone:
            raise UserError(_("La compañia debe tener un número de teléfono."))
        elif not document.company_id.country_id:
            raise UserError(_("La compañia debe tener un país."))
        elif not document.company_id.state_id:
            raise UserError(_("La compañia debe tener una provincia."))
        elif not document.company_id.county_id:
            raise UserError(_("La compañia debe tener un cantón."))
        elif not document.company_id.district_id:
            raise UserError(_("La compañia debe tener un distrito."))
        elif not document.company_id.neighborhood_id:
            raise UserError(_("La compañia debe tener un barrio."))
        elif not document.company_id.email:
            raise UserError(_("La compañia debe tener un email."))
        elif not document.company_id.identification_id:
            raise UserError(_("La compañia debe tener un tipo de documento."))
        elif not document.company_id.vat:
            raise UserError(_("La compañia debe tener un número de documento de identidad."))
    else:
        pass

def gen(document):
    # metodo para validaciones
    validations(document)
    issuer = document.company_id
    receiver = document.partner_id

    #TODO: PARA EL CASO DE POS
    if 'pos_reference' in document:
        template = DOCUMENT_TYPE_TO_TEMPLATE[type_template[document.tipo_documento]]
        args = {
            "document": document,
            "issuer": issuer,
            "receiver": receiver,
            "lines": document.lines,
            #"activity_code": document.company_id.pos_activity_id.code,
            "activity_code": issuer.activity_ids[0].code,
            "currency_rate": document.currency_rate,
            "notes": None,
            "reference": document.pos_order_id,
            "reference_code": document.reference_code_id,
        }
    #TODO: PARA COMPROBANTES DE CONTABILIDAD
    else:
        template = DOCUMENT_TYPE_TO_TEMPLATE[document.tipo_documento]
        if document.tipo_documento == "FEC":  # TODO only in this case?
            (issuer, receiver) = (receiver, issuer)
        args = {
            "document": document,
            "issuer": issuer,
            "receiver": receiver,
            "lines": document.invoice_line_ids,
            "activity_code": document.activity_id.code,
            "currency_rate": document.currency_rate_usd_crc,
            "notes": document.narration,
            "reference": document.invoice_id,
            "reference_code": document.reference_code_id,
        }

    render = gen_from_template(template, **args)
    return render


def gen_from_template(
    template,
    document,
    issuer,
    receiver,
    activity_code,
    lines,
    currency_rate,
    notes,
    reference=None,
    reference_code=None,
):
    lineas = document._get_lines_xml(lines)
    amounts = document.get_amounts(lineas)
    phone_obj_issuer = phonenumbers.parse(
        issuer.phone, issuer.country_id and issuer.country_id.code
    )
    if 'pos_reference' in document:
        render = template.render(
            document=document,
            activity_code=activity_code,
            issuer=issuer,
            receiver=receiver,
            phone_obj_issuer=None if document.tipo_documento =='TE' else phone_obj_issuer,
            phone_obj_receiver=None,
            lines=lines,
            amounts=amounts,
            currency_rate=currency_rate,
            notes=notes,
            reference=reference,
            reference_code=reference_code,
        )
    else:
        phone_obj_receiver = phonenumbers.parse(
            receiver.phone,
            (receiver.country_id or issuer.country_id) and (receiver.country_id.code or issuer.country_id.code)
        )
        render = template.render(
            document=document,
            activity_code=activity_code,
            issuer=issuer,
            receiver=receiver,
            phone_obj_issuer=phone_obj_issuer,
            phone_obj_receiver=phone_obj_receiver,
            lines=lineas,
            amounts=amounts,
            currency_rate=currency_rate,
            notes=notes,
            reference=reference,
            reference_code=reference_code,
        )

    return render
