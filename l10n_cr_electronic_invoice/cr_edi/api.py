import base64
import json

import requests

from . import abstract


def _send_post(client_id: str, token: str, data: dict):
    endpoint = abstract.Environment.get(client_id).reception_endpoint
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json",
    }
    data_json = json.dumps(data)
    response = _requests_no_exception("POST", endpoint, data=data_json, headers=headers)
    return response


def _get_text_from_response(response: requests.Response) -> str:
    ok = 200 <= response.status_code <= 299
    error_message = "{} {}".format(
        response.headers.get("X-Error-Cause", "Unknown"),
        response.headers.get("validation-exception", ""),
    )
    text = response.text if ok else error_message
    return text


def _process_response(response: requests.Response) -> dict:
    processed = {
        "status": response.status_code,
        "text": _get_text_from_response(response),
    }
    if response.text:
        processed["ind-estado"] = response.json().get("ind-estado")
        processed["respuesta-xml"] = response.json().get("respuesta-xml")
    return processed


def _requests_no_exception(request_type: str, endpoint: str, **args):
    try:
        response = requests.request(request_type, endpoint, **args)
    except requests.exceptions.RequestException as exception:
        processed = {"status": -1, "text": "Exception {}".format(exception)}
    else:
        processed = _process_response(response)
    return processed


def _encode_and_decode(data: str) -> str:
    return base64.b64encode(data).decode()


def send_xml(client_id, token, xml, date, electronic_number, issuer, receiver):
    data = {
        "clave": electronic_number,
        "fecha": date,
        "emisor": {
            "tipoIdentificacion": issuer.identification_id.code,
            "numeroIdentificacion": issuer.vat,
        },
        "comprobanteXml": _encode_and_decode(xml),
    }
    if receiver:
        data["receptor"] = {
            "tipoIdentificacion": receiver.identification_id.code,
            "numeroIdentificacion": receiver.vat,
        }

    response_processed = _send_post(client_id, token, data)
    return response_processed


def send_message(inv, date_cr, xml, token, client_id):
    data = {
        "clave": inv.number_electronic,
        "consecutivoReceptor": inv.consecutive_number_receiver,
        "fecha": date_cr,
        "emisor": {
            "tipoIdentificacion": str(inv.partner_id.identification_id.code),
            "numeroIdentificacion": inv.partner_id.vat,
        },
        "receptor": {
            "tipoIdentificacion": str(inv.company_id.identification_id.code),
            "numeroIdentificacion": inv.company_id.vat,
        },
        "comprobanteXml": _encode_and_decode(xml),
    }

    response_processed = _send_post(client_id, token, data)
    return response_processed


def query_document(clave, token, client_id):
    environment = abstract.Environment.get(client_id)
    endpoint = "{}/{}".format(environment.reception_endpoint, clave)
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response_processed = _requests_no_exception("GET", endpoint, headers=headers)
    return response_processed
