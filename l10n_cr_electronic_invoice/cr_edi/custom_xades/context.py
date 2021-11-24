# Lib to sign Xades-EPES xml docx
# 2019 por Ricardo Vong <rvong@indelsacr.com>
# Based on Tobella's original Xades implementation

import datetime
import logging
import random
import re

import pytz
import xmlsig
from xades import constants, template

logger = logging.getLogger(__name__)


URL_ESCAPE_PATTERN = re.compile("[\r\n]")


def create_xades_epes_signature(sign_date=None):
    sign_date = sign_date or datetime.datetime.now(pytz.timezone("UTC"))
    min_val = 1
    max_val = 9999

    signature_id = "Signature-{:04d}".format(random.randint(min_val, max_val))
    signed_properties_id = "SignedProperties-" + signature_id
    key_info_id = "KeyInfoId-" + signature_id
    reference_id = "Reference-{:04d}".format(random.randint(min_val, max_val))

    signature = xmlsig.template.create(
        xmlsig.constants.TransformInclC14N,
        xmlsig.constants.TransformRsaSha256,
        signature_id,
    )

    # Reference to Document Digest
    ref = xmlsig.template.add_reference(
        signature, xmlsig.constants.TransformSha256, reference_id, uri=""
    )
    xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)
    xmlsig.template.add_transform(ref, xmlsig.constants.TransformInclC14N)
    # Reference to KeyInfo Digest
    ref = xmlsig.template.add_reference(
        signature,
        xmlsig.constants.TransformSha256,
        "ReferenceKeyInfo",
        uri="#" + key_info_id,
    )
    xmlsig.template.add_transform(ref, xmlsig.constants.TransformInclC14N)
    # Reference to the SignedProperties Digest
    ref = xmlsig.template.add_reference(
        signature,
        xmlsig.constants.TransformSha256,
        uri="#" + signed_properties_id,
        uri_type="http://uri.etsi.org/01903#SignedProperties",
    )
    xmlsig.template.add_transform(ref, xmlsig.constants.TransformInclC14N)

    ki = xmlsig.template.ensure_key_info(signature, name=key_info_id)
    x509_data = xmlsig.template.add_x509_data(ki)

    xmlsig.template.x509_data_add_certificate(x509_data)
    xmlsig.template.add_key_value(ki)
    qualifying = template.create_qualifying_properties(signature, "XadesObjects", "xades")
    props = template.create_signed_properties(
        qualifying, name=signed_properties_id, datetime=sign_date
    )
    # Manually add DataObjectFormat
    data_obj = xmlsig.utils.create_node("SignedDataObjectProperties", props, ns=constants.EtsiNS)
    obj_format = xmlsig.utils.create_node("DataObjectFormat", data_obj, ns=constants.EtsiNS)
    obj_format.set("ObjectReference", "#" + reference_id)
    xmlsig.utils.create_node("MimeType", obj_format, ns=constants.EtsiNS).text = "text/xml"
    xmlsig.utils.create_node("Encoding", obj_format, ns=constants.EtsiNS).text = "UTF-8"
    return signature
