import base64
import datetime
import logging
from threading import Lock
from xml.sax.saxutils import escape

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_cr_electronic_invoice import cr_edi

lock = Lock()

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _name = "pos.order"
    _inherit = "pos.order", "mail.thread"

    @api.model
    def sequence_number_sync(self, vals):
        tipo_documento = vals.get("tipo_documento", False)
        sequence = vals.get("sequence", False)
        sequence = int(sequence) if sequence else False
        if vals.get("session_id") and sequence:
            session = self.env["pos.session"].sudo().browse(vals["session_id"])
            if (
                tipo_documento == "FE"
                and sequence >= session.config_id.FE_sequence_id.number_next_actual
            ):
                session.config_id.FE_sequence_id.number_next_actual = sequence + 1
            elif (
                tipo_documento == "TE"
                and sequence >= session.config_id.TE_sequence_id.number_next_actual
            ):
                session.config_id.TE_sequence_id.number_next_actual = sequence + 1

    @api.model
    def _order_fields(self, ui_order):
        vals = super(PosOrder, self)._order_fields(ui_order)
        vals["tipo_documento"] = ui_order.get("tipo_documento")
        vals["sequence"] = ui_order.get("sequence")
        vals["number_electronic"] = ui_order.get("number_electronic")
        return vals

    @api.model
    def create(self, vals):
        session = self.env["pos.session"].sudo().browse(vals["session_id"])
        sequence = cr_edi.utils.compute_full_sequence(
            session.config_id.sucursal,
            session.config_id.terminal,
            vals["tipo_documento"],
            session.config_id.TE_sequence_id.next_by_id(),
        )
        vals["sequence"] = sequence
        number = cr_edi.utils.get_number_electronic(self.env.user, sequence)
        vals["number_electronic"] = number
        order = super(PosOrder, self).create(vals)
        return order

    number_electronic = fields.Char(
        string="Número electrónico",
        required=False,
        copy=False,
        index=True,
    )
    date_issuance = fields.Char(
        string="Fecha de emisión",
        required=False,
        copy=False,
    )
    state_tributacion = fields.Selection(
        selection=[
            ("aceptado", "Aceptado"),
            ("rechazado", "Rechazado"),
            ("rejected", "Rechazado2"),
            ("no_encontrado", "No encontrado"),
            ("recibido", "Recibido"),
            ("firma_invalida", "Firma Inválida"),
            ("error", "Error"),
            ("procesando", "Procesando"),
        ],
        string="Estado FE",
        copy=False,
    )
    reference_code_id = fields.Many2one(
        comodel_name="reference.code",
        string="Código de referencia",
        required=False,
    )
    pos_order_id = fields.Many2one(
        comodel_name="pos.order",
        string="Documento de referencia",
        required=False,
        copy=False,
    )
    xml_respuesta_tributacion = fields.Binary(
        string="Respuesta Tributación XML",
        required=False,
        copy=False,
        attachment=True,
    )
    fname_xml_respuesta_tributacion = fields.Char(
        string="Nombre de archivo XML Respuesta Tributación",
        required=False,
        copy=False,
    )
    xml_comprobante = fields.Binary(
        string="Comprobante XML",
        required=False,
        copy=False,
        attachment=True,
    )
    fname_xml_comprobante = fields.Char(
        string="Nombre de archivo Comprobante XML",
        required=False,
        copy=False,
    )
    state_email = fields.Selection(
        selection=[
            ("no_email", "Sin cuenta de correo"),
            ("sent", "Enviado"),
            ("fe_error", "Error FE"),
        ],
        string="Estado email",
        copy=False,
    )
    error_count = fields.Integer(
        string="Cantidad de errores",
        required=False,
        default="0",
    )
    tipo_documento = fields.Selection(
        selection=[
            ("FE", "Factura Electrónica Normal"),
            ("TE", "Tiquete Electrónico"),
            ("NC", "Nota de Crédito"),
        ],
        string="Tipo Comprobante",
        required=False,
        default="FE",
        help="Indica el tipo de documento de acuerdo a la clasificación del Ministerio de Hacienda",
    )
    sequence = fields.Char(
        string="Consecutivo",
        readonly=True,
    )
    _sql_constraints = [
        (
            "number_electronic_uniq",
            "unique (number_electronic)",
            "La clave de comprobante debe ser única",
        ),
    ]

    def action_pos_order_paid(self):
        for order in self:
            if order.pos_order_id:
                order.name = order.session_id.config_id.return_sequence_id._next()
        return super(PosOrder, self).action_pos_order_paid()

    def refund(self):
        po = self.env["pos.order"]
        reference_code_id = self.env["reference.code"].search([("code", "=", "01")], limit=1)
        current_session = self.env["pos.session"].search(
            [
                ("state", "!=", "closed"),
                ("user_id", "=", self.env.uid),
                ("name", "not like", "RESCUE"),
            ],
            limit=1,
        )
        if not current_session:
            raise UserError(
                _(
                    "To return product(s), you need to open a session that will be used to register the refund."
                )
            )
        for order in self:
            clone = order.copy(
                {
                    "name": order.name + _(" REFUND"),
                    "session_id": current_session.id,
                    "date_order": fields.Datetime.now(),
                    "pos_order_id": order.id,
                    "reference_code_id": reference_code_id.id,
                }
            )
            po += clone
        for clone in po:
            for order_line in clone.lines:
                order_line.write({"qty": -order_line.qty})
        return {
            "name": _("Return Products"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "pos.order",
            "res_id": po.ids[0],
            "view_id": False,
            "context": self.env.context,
            "type": "ir.actions.act_window",
            "target": "current",
        }

    @api.model
    def _consultahacienda_pos(self, max_orders=10):
        pos_orders = self.env["pos.order"].search(
            [
                ("state", "in", ("paid", "done", "invoiced")),
                ("number_electronic", "!=", False),
                ("state_tributacion", "in", ("recibido", "procesando")),
            ],
            limit=max_orders,
        )
        total_orders = len(pos_orders)
        current_order = 0
        _logger.info("MAB - Consulta Hacienda - POS Orders to check: %s", total_orders)
        for doc in pos_orders:
            current_order += 1
            _logger.info(
                "MAB - Consulta Hacienda - POS Order %s / %s",
                current_order,
                total_orders,
            )
            token_m_h = cr_edi.auth.get_token(
                internal_id=doc.company_id.id,
                username=doc.company_id.frm_ws_identificador,
                password=doc.company_id.frm_ws_password,
                client_id=doc.company_id.frm_ws_ambiente,
            )
            if doc.number_electronic and len(doc.number_electronic) == 50:
                response_json = cr_edi.api.query_document(
                    clave=doc.number_electronic,
                    token=token_m_h,
                    client_id=doc.company_id.frm_ws_ambiente,
                )
                status = response_json["status"]
                if status == 200:
                    estado_m_h = response_json.get("ind-estado")
                elif status == 400:
                    estado_m_h = response_json.get("ind-estado")
                    _logger.error(
                        "MAB - Error: %s Documento:%s no encontrado en Hacienda",
                        estado_m_h,
                        doc.number_electronic,
                    )
                else:
                    _logger.error("MAB - Error inesperado en Consulta Hacienda - Abortando")
                    return
                if estado_m_h == "aceptado":
                    doc.state_tributacion = estado_m_h
                    doc.fname_xml_respuesta_tributacion = "AHC_" + doc.number_electronic + ".xml"
                    doc.xml_respuesta_tributacion = response_json.get("respuesta-xml")
                    if doc.partner_id and doc.partner_id.email:
                        email_template = self.env.ref("fecr_pos.email_template_pos_invoice", False)
                        attachment = self.env["ir.attachment"].search(
                            [
                                ("res_model", "=", "pos.order"),
                                ("res_id", "=", doc.id),
                                ("res_field", "=", "xml_comprobante"),
                            ],
                            limit=1,
                        )
                        attachment.name = doc.fname_xml_comprobante
                        attachment.datas_fname = doc.fname_xml_comprobante
                        attachment_resp = self.env["ir.attachment"].search(
                            [
                                ("res_model", "=", "pos.order"),
                                ("res_id", "=", doc.id),
                                ("res_field", "=", "xml_respuesta_tributacion"),
                            ],
                            limit=1,
                        )
                        attachment_resp.name = doc.fname_xml_respuesta_tributacion
                        attachment_resp.datas_fname = doc.fname_xml_respuesta_tributacion
                        email_template.attachment_ids = [
                            (6, 0, [attachment.id, attachment_resp.id])
                        ]
                        email_template.with_context(type="binary", default_type="binary").send_mail(
                            doc.id, raise_exception=False, force_send=True
                        )
                        email_template.attachment_ids = [(5)]
                        doc.state_email = "sent"
                    else:
                        doc.state_email = "no_email"
                        _logger.info("email no enviado - cliente no definido")
                elif estado_m_h == "firma_invalida":
                    if doc.error_count > 10:
                        doc.state_tributacion = estado_m_h
                        doc.fname_xml_respuesta_tributacion = (
                            "AHC_" + doc.number_electronic + ".xml"
                        )
                        doc.xml_respuesta_tributacion = response_json.get("respuesta-xml")
                        doc.state_email = "fe_error"
                        _logger.info("email no enviado - factura rechazada")
                    else:
                        doc.error_count += 1
                        doc.state_tributacion = "procesando"
                elif estado_m_h in ("rechazado", "rejected"):
                    doc.state_tributacion = estado_m_h
                    doc.fname_xml_respuesta_tributacion = "AHC_" + doc.number_electronic + ".xml"
                    doc.xml_respuesta_tributacion = response_json.get("respuesta-xml")
                    doc.state_email = "fe_error"
                    _logger.info("email no enviado - factura rechazada")
                elif estado_m_h == "error":
                    doc.state_tributacion = estado_m_h
                    doc.state_email = "fe_error"
                else:
                    if doc.error_count > 10:
                        doc.state_tributacion = "error"
                    elif doc.error_count < 4:
                        doc.error_count += 1
                        doc.state_tributacion = "procesando"
                    else:
                        doc.error_count += 1
                        doc.state_tributacion = ""
                    _logger.error(
                        "MAB - Consulta Hacienda - POS Order not found: %s",
                        doc.number_electronic,
                    )
            else:
                doc.state_tributacion = "error"
                _logger.error(
                    "MAB - POS Order %s  - x Number Electronic: %s formato incorrecto",
                    doc.name,
                    doc.number_electronic,
                )
        _logger.info("MAB - Consulta Hacienda POS- Finalizad Exitosamente")

    @api.model
    def _reenviacorreos_pos(self, max_orders=1):
        pos_orders = self.env["pos.order"].search(
            [
                ("state", "in", ("paid", "done", "invoiced")),
                ("date_order", ">=", "2018-09-01"),
                ("number_electronic", "!=", False),
                ("state_email", "=", False),
                ("state_tributacion", "=", "aceptado"),
            ],
            limit=max_orders,
        )
        total_orders = len(pos_orders)
        current_order = 0
        _logger.info("MAB - Reenvia Correos- POS Orders to send: %s", total_orders)
        for doc in pos_orders:
            current_order += 1
            _logger.info(
                "MAB - Reenvia Correos- POS Order %s - %s / %s",
                doc.name,
                current_order,
                total_orders,
            )
            if (
                doc.partner_id.email
                and not doc.partner_id.opt_out
                and doc.state_tributacion == "aceptado"
            ):
                comprobante = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "pos.order"),
                        ("res_id", "=", doc.id),
                        ("res_field", "=", "xml_comprobante"),
                    ],
                    limit=1,
                )
                if not comprobante:
                    _logger.error("Email no enviado - tiquete sin xml doc: %s", doc.name)
                    continue
                try:
                    comprobante.name = doc.fname_xml_comprobante
                except:
                    comprobante.name = "FE_" + doc.number_electronic + ".xml"
                comprobante.datas_fname = comprobante.name
                respuesta = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "pos.order"),
                        ("res_id", "=", doc.id),
                        ("res_field", "=", "xml_respuesta_tributacion"),
                    ],
                    limit=1,
                )
                respuesta.name = doc.fname_xml_respuesta_tributacion
                respuesta.datas_fname = doc.fname_xml_respuesta_tributacion
                email_template = self.env.ref("fecr_pos.email_template_pos_invoice", False)
                email_template.attachment_ids = [(6, 0, [comprobante.id, respuesta.id])]
                email_template.with_context(type="binary", default_type="binary").send_mail(
                    doc.id, raise_exception=False, force_send=True
                )
                doc.state_email = "sent"
            elif doc.state_tributacion in ("rechazado", "rejected"):
                doc.state_email = "fe_error"
                _logger.error("email no enviado - factura rechazada. Doc: %s", doc.name)
            else:
                doc.state_email = "no_email"
                _logger.error("email no enviado - cuenta no definida. Doc: %s", doc.name)
        _logger.info("MAB - Reenvia Correos - Finalizado")

    @api.model
    def _validahacienda_pos(self, max_orders=10, no_partner=True):
        pos_orders = self.env["pos.order"].search(
            [
                ("state", "in", ("paid", "done", "invoiced")),
                "|",
                (no_partner, "=", True),
                ("partner_id", "!=", False),
                ("state_tributacion", "=", False),
            ],
            order="date_order",
            limit=max_orders,
        )
        total_orders = len(pos_orders)
        current_order = 0
        _logger.info("MAB - Valida Hacienda - POS Orders to check: %s", total_orders)
        for doc in pos_orders:
            current_order += 1
            _logger.info("MAB - Valida Hacienda - POS Order %s / %s", current_order, total_orders)
            docName = doc.number_electronic
            if not docName:
                continue
            if not docName.isdigit() or doc.company_id.frm_ws_ambiente == "disabled":
                _logger.warning("MAB - Valida Hacienda - skipped Invoice %s", docName)
                continue
            if not doc.xml_comprobante:
                if not doc.pos_order_id:
                    if doc.amount_total < 0:
                        doc.state_tributacion = "error"
                        _logger.error(
                            "MAB - Error documento %s tiene monto negativo pero no tiene documento referencia",
                            doc.number_electronic,
                        )
                        continue
                else:
                    if doc.amount_total >= 0:
                        doc.tipo_documento = "ND"
                        # razon_referencia = "nota debito"
                    else:
                        doc.tipo_documento = "NC"
                        # tipo_documento_referencia = "FE"
                        # numero_documento_referencia = doc.pos_order_id.number_electronic
                        # codigo_referencia = doc.reference_code_id.code
                        # razon_referencia = "nota credito"
                    # numero_documento_referencia = doc.pos_order_id.number_electronic
                    # fecha_emision_referencia = doc.pos_order_id.date_issuance
                    # codigo_referencia = doc.reference_code_id.code
                now_utc = datetime.datetime.now(pytz.timezone("UTC"))
                now_cr = now_utc.astimezone(pytz.timezone("America/Costa_Rica"))
                dia = docName[3:5]
                mes = docName[5:7]
                anno = docName[7:9]
                date_cr = now_cr.strftime("20" + anno + "-" + mes + "-" + dia + "T%H:%M:%S-06:00")
                codigo_seguridad = docName[-8:]
                if (
                    not doc.statement_ids
                    or not doc.statement_ids[0].statement_id
                    or not doc.statement_ids[0].statement_id.journal_id
                    or not doc.statement_ids[0].statement_id.journal_id.pos_payment_method_ids.ids
                ):
                    _logger.warning(
                        "MAB 001 - codigo seguridad : %s  -- Pedido: %s Metodo de pago de diario no definido, utilizando efectivo",
                        codigo_seguridad,
                        docName,
                    )
                # sale_conditions = "01"
                currency_rate = 1
                lines = dict()
                otros_cargos = dict()
                otros_cargos_id = 0
                line_number = 0
                total_servicio_gravado = 0.0
                total_servicio_exento = 0.0
                # total_servicio_exonerado = 0.0  # TODO use
                total_mercaderia_gravado = 0.0
                total_mercaderia_exento = 0.0
                # total_mercaderia_exonerado = 0.0  # TODO use
                total_descuento = 0.0
                total_impuestos = 0.0
                base_subtotal = 0.0
                total_otros_cargos = 0.0
                for line in doc.lines:
                    line_number += 1
                    price = line.price_unit * (1 - line.discount / 100.0)
                    qty = abs(line.qty)
                    if not qty:
                        continue
                    fpos = line.order_id.fiscal_position_id
                    tax_ids = (
                        fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id)
                        if fpos
                        else line.tax_ids
                    )
                    line_taxes = tax_ids.compute_all(
                        price,
                        line.order_id.pricelist_id.currency_id,
                        1,
                        product=line.product_id,
                        partner=line.order_id.partner_id,
                    )
                    # ajustar para IVI
                    price_unit = round(
                        line_taxes["total_excluded"] / (1 - line.discount / 100.0), 5
                    )
                    base_line = abs(round(price_unit * qty, 5))
                    subtotal_line = abs(round(price_unit * qty * (1 - line.discount / 100.0), 5))
                    dline = {
                        "cantidad": qty,
                        "unidadMedida": line.product_id and line.product_id.uom_id.code or "Sp",
                        "cabys_code": line.product_id.cabys_id.code,
                        "detalle": escape(line.product_id.name[:159]),
                        "precioUnitario": price_unit,
                        "montoTotal": base_line,
                        "subtotal": subtotal_line,
                    }
                    if line.discount:
                        descuento = abs(round(base_line - subtotal_line, 5))
                        total_descuento += descuento
                        dline["montoDescuento"] = descuento
                        dline["naturalezaDescuento"] = "Descuento Comercial"
                    taxes = dict()
                    _line_tax = 0.0
                    if tax_ids:
                        tax_index = 0
                        taxes_lookup = {}
                        for i in tax_ids:
                            taxes_lookup[i.id] = {
                                "tax_code": i.tax_code,
                                "tarifa": i.amount,
                                "iva_tax_desc": i.iva_tax_desc,
                                "iva_tax_code": i.iva_tax_code,
                            }
                        tax_amount = 0
                        for i in line_taxes["taxes"]:
                            if taxes_lookup[i["id"]]["tax_code"] == "service":
                                total_otros_cargos += tax_amount
                            elif taxes_lookup[i["id"]]["tax_code"] != "00":
                                tax_index += 1
                                tax_amount = abs(round(i["amount"], 5) * qty)
                                _line_tax += tax_amount
                                taxes[tax_index] = {
                                    "codigo": taxes_lookup[i["id"]]["tax_code"],
                                    "tarifa": taxes_lookup[i["id"]]["tarifa"],
                                    "monto": tax_amount,
                                    "iva_tax_desc": taxes_lookup[i["id"]]["iva_tax_desc"],
                                    "iva_tax_code": taxes_lookup[i["id"]]["iva_tax_code"],
                                }
                    dline["impuesto"] = taxes
                    dline["impuestoNeto"] = _line_tax
                    if line.product_id and line.product_id.type == "service":
                        if taxes:
                            total_servicio_gravado += base_line
                            total_impuestos += _line_tax
                        else:
                            total_servicio_exento += base_line
                    else:
                        if taxes:
                            total_mercaderia_gravado += base_line
                            total_impuestos += _line_tax
                        else:
                            total_mercaderia_exento += base_line
                    base_subtotal += subtotal_line
                    dline["montoTotalLinea"] = subtotal_line + _line_tax
                    lines[line_number] = dline
                if total_otros_cargos:
                    otros_cargos_id = 1
                    tax_amount = abs(round(i["amount"], 5) * qty)
                    otros_cargos[otros_cargos_id] = {
                        "TipoDocumento": taxes_lookup[i["id"]]["iva_tax_code"],
                        "Detalle": escape(taxes_lookup[i["id"]]["iva_tax_desc"]),
                        "MontoCargo": total_otros_cargos,
                    }
                doc.date_issuance = date_cr
                # invoice_comments = ""
                xml_string_builder = cr_edi.gen_xml.gen(doc, currency_rate)
                xml_to_sign = str(xml_string_builder)
                xml_firmado = cr_edi.utils.sign_xml(
                    cert=doc.company_id.signature,
                    pin=doc.company_id.frm_pin,
                    xml=xml_to_sign,
                )
                doc.fname_xml_comprobante = doc.tipo_documento + "_" + docName + ".xml"
                doc.xml_comprobante = base64.encodebytes(xml_firmado)
                _logger.info("MAB - SIGNED XML:%s", doc.fname_xml_comprobante)
            token_m_h = cr_edi.auth.get_token(
                internal_id=doc.company_id.id,
                username=doc.company_id.frm_ws_identificador,
                password=doc.company_id.frm_ws_password,
                client_id=doc.company_id.frm_ws_ambiente,
            )
            response_json = cr_edi.api.send_xml(
                doc.company_id.frm_ws_ambiente,
                token_m_h,
                doc.xml_comprobante,
                date_cr,
                doc.electronic_number,
                doc.company_id,
                doc.partner_id,
            )
            response_status = response_json.get("status")
            response_text = response_json.get("text")
            if 200 <= response_status <= 299:
                doc.state_tributacion = "procesando"
            else:
                if response_text.find("ya fue recibido anteriormente") != -1:
                    doc.state_tributacion = "procesando"
                    doc.message_post(
                        subject=_("Error"),
                        body=_("Ya recibido anteriormente, se pasa a consultar"),
                    )
                elif doc.error_count > 10:
                    doc.message_post(subject=_("Error"), body=response_text)
                    doc.state_tributacion = "error"
                    _logger.error(
                        "MAB - Invoice: %s  Status: %s Error sending XML: %s",
                        doc.name,
                        response_status,
                        response_text,
                    )
                else:
                    doc.error_count += 1
                    doc.state_tributacion = "procesando"
                    doc.message_post(subject=_("Error"), body=response_text)
                    _logger.error(
                        "MAB - Invoice: %s  Status: %s Error sending XML: %s",
                        doc.name,
                        response_status,
                        response_text,
                    )
        _logger.info("MAB 014 - Valida Hacienda POS- Finalizado Exitosamente")
