import base64
import pkgutil
import random
from datetime import datetime

import jinja2
import OpenSSL
import phonenumbers
import pytz
import xades
import xmlsig
from lxml import etree
import re
from . import abstract
from .custom_xades.context import create_xades_epes_signature


def get_time_cr(as_obj=False):
    """Return current time in Costa Rica in ISO-Format

    Returns:
        str: current time in Costa Rica in ISO-Format
    """
    now_cr = datetime.now(pytz.timezone("America/Costa_Rica"))
    if as_obj:
        return now_cr
    iso_str = now_cr.isoformat()
    return iso_str


def limit(string, max_chars):
    """Truncate a string to the `max_chars` amount ouf chars and append `...` at the end of it if is truncated

    Args:
        string (str): String to limitate
        max_chars (integer): Amount of chars wanted

    Returns:
        str: The original string truncated
    """
    return (string[: max_chars - 3] + "...") if len(string) > max_chars else string


def compute_full_sequence(branch, terminal, doc_type, sequence):
    branch = str(branch)
    terminal = str(terminal)
    doc_type = str(doc_type)
    sequence = str(sequence)
    doc_type_code = abstract.Document.TYPE_TO_CODE[doc_type]

    if not abstract.Sequence.valid(sequence):
        raise Exception("The sequence must have 10 digits")

    branch_filled = branch.zfill(3)
    terminal_filled = terminal.zfill(5)

    full_sequence = branch_filled + terminal_filled + doc_type_code + sequence
    return full_sequence


def get_number_electronic(
    issuer,
    full_sequence,
    situation_code=abstract.Voucher.TYPE_TO_CODE["normal"],
):
    """Generate Number Electronic

    Args:
        issuer (res.company/res.partner): Issuer
        full_sequence (str): Sequence used to generate Number Electronic (use compute_full_sequence to generate it)
        situation_code (str, optional): Situation code. Defaults to Voucher.TYPE_TO_CODE["normal"].

    Returns:
        [type]: [description]
    """
    phone_obj_issuer = phonenumbers.parse(
        issuer.phone, issuer.country_id and issuer.country_id.code
    )
    cur_date = get_time_cr(as_obj=True).strftime("%d%m%y")
    random_digits = str(random.randint(1, 99999999)).zfill(8)
    number_electronic = (
        str(phone_obj_issuer.country_code)
        + cur_date
        + str(issuer.vat).zfill(12)
        + full_sequence
        + situation_code
        + random_digits
    )
    return number_electronic


def get_template(path: str) -> jinja2.Template:
    """Get jinja2.Template from local path and trim extra spaces

    Args:
        path (str): Template .jinja path

    Returns:
        jinja2.Template: Template
    """
    template = jinja2.Template(
        pkgutil.get_data(__name__, "templates/" + path).decode(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return template


def sign_xml(cert, pin, xml):
    """Sign an XML using XAdES

    Args:
        cert (binary): Certificate
        pin (str): PIN to decrypt cert
        xml (str): XML to be signed

    Returns:
        [str]: XML signed
    """
    policy_id = "https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.2/ResolucionComprobantesElectronicosDGT-R-48-2016_4.2.pdf"
    #xml = re.sub(r'&([^a-zA-Z#])', r'&amp;\1', xml)
    xml = xml.replace('&', '&amp;')
    root = etree.fromstring(xml)
    signature = create_xades_epes_signature()
    policy = xades.policy.GenericPolicyId(
        identifier=policy_id,
        name=u"Politica de Firma Factura",
        hash_method=xmlsig.constants.TransformSha1,
    )
    root.append(signature)
    ctx = xades.XAdESContext(policy)
    certificate = OpenSSL.crypto.load_pkcs12(base64.b64decode(cert), pin)
    ctx.load_pkcs12(certificate)
    ctx.sign(signature)
    signed = etree.tostring(
        root,
        encoding="UTF-8",
        method="xml",
        xml_declaration=True,
        with_tail=False,
    )
    return signed
