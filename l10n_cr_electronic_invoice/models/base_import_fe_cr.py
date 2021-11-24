import logging
import mimetypes
from io import StringIO
from tempfile import NamedTemporaryFile

from lxml import etree

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round

logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
    from PyPDF2.generic import NameObject
except ImportError:
    logger.debug("Cannot import PyPDF2")


class BaseCRFe(models.AbstractModel):
    _name = "base.fe_cr"
    _description = "Common methods to generate and parse Costa Rican Electronic Document files"

    @api.model
    def _fe_cr_add_country(self, country, parent_node, ns, version="2.1"):
        country_root = etree.SubElement(parent_node, ns["cac"] + "Country")
        country_code = etree.SubElement(country_root, ns["cbc"] + "IdentificationCode")
        country_code.text = country.code
        country_name = etree.SubElement(country_root, ns["cbc"] + "Name")
        country_name.text = country.name

    @api.model
    def _fe_cr_add_address(self, partner, node_name, parent_node, ns, version="2.1"):
        address = etree.SubElement(parent_node, ns["cac"] + node_name)
        if partner.street:
            streetname = etree.SubElement(address, ns["cbc"] + "StreetName")
            streetname.text = partner.street
        if partner.street2:
            addstreetname = etree.SubElement(address, ns["cbc"] + "AdditionalStreetName")
            addstreetname.text = partner.street2
        if hasattr(partner, "street3") and partner.street3:
            blockname = etree.SubElement(address, ns["cbc"] + "BlockName")
            blockname.text = partner.street3
        if partner.city:
            city = etree.SubElement(address, ns["cbc"] + "CityName")
            city.text = partner.city
        if partner.zip:
            zip_var = etree.SubElement(address, ns["cbc"] + "PostalZone")
            zip_var.text = partner.zip
        if partner.state_id:
            state = etree.SubElement(address, ns["cbc"] + "CountrySubentity")
            state.text = partner.state_id.name
            state_code = etree.SubElement(address, ns["cbc"] + "CountrySubentityCode")
            state_code.text = partner.state_id.code
        if partner.country_id:
            self._fe_cr_add_country(partner.country_id, address, ns, version=version)
        else:
            logger.warning("UBL: missing country on partner {}".format(partner.name))

    @api.model
    def _fe_cr_get_contact_id(self, partner):
        return False

    @api.model
    def _fe_cr_add_contact(self, partner, parent_node, ns, node_name="Contact", version="2.1"):
        contact = etree.SubElement(parent_node, ns["cac"] + node_name)
        contact_id_text = self._fe_cr_get_contact_id(partner)
        if contact_id_text:
            contact_id = etree.SubElement(contact, ns["cbc"] + "ID")
            contact_id.text = contact_id_text
        if partner.parent_id:
            contact_name = etree.SubElement(contact, ns["cbc"] + "Name")
            contact_name.text = partner.name
        phone = partner.phone or partner.commercial_partner_id.phone
        if phone:
            telephone = etree.SubElement(contact, ns["cbc"] + "Telephone")
            telephone.text = phone
        fax = partner.fax or partner.commercial_partner_id.fax
        if fax:
            telefax = etree.SubElement(contact, ns["cbc"] + "Telefax")
            telefax.text = fax
        email = partner.email or partner.commercial_partner_id.email
        if email:
            electronicmail = etree.SubElement(contact, ns["cbc"] + "ElectronicMail")
            electronicmail.text = email

    @api.model
    def _fe_cr_add_language(self, lang_code, parent_node, ns, version="2.1"):
        langs = self.env["res.lang"].search([("code", "=", lang_code)])
        if not langs:
            return
        lang = langs[0]
        lang_root = etree.SubElement(parent_node, ns["cac"] + "Language")
        lang_name = etree.SubElement(lang_root, ns["cbc"] + "Name")
        lang_name.text = lang.name
        lang_code = etree.SubElement(lang_root, ns["cbc"] + "LocaleCode")
        lang_code.text = lang.code

    @api.model
    def _fe_cr_get_party_identification(self, commercial_partner):
        """This method is designed to be inherited in localisation modules
        Should return a dict with key=SchemeName, value=Identifier"""
        return {}

    @api.model
    def _fe_cr_add_party_identification(self, commercial_partner, parent_node, ns, version="2.1"):
        id_dict = self._fe_cr_get_party_identification(commercial_partner)
        if id_dict:
            party_identification = etree.SubElement(parent_node, ns["cac"] + "PartyIdentification")
            for scheme_name, party_id_text in id_dict.items():
                party_identification_id = etree.SubElement(
                    party_identification, ns["cbc"] + "ID", schemeName=scheme_name
                )
                party_identification_id.text = party_id_text
        return

    @api.model
    def _fe_cr_get_tax_scheme_dict_from_partner(self, commercial_partner):
        tax_scheme_dict = {
            "id": "VAT",
            "name": False,
            "type_code": False,
        }
        return tax_scheme_dict

    @api.model
    def _fe_cr_add_party_tax_scheme(self, commercial_partner, parent_node, ns, version="2.1"):
        if commercial_partner.vat:
            party_tax_scheme = etree.SubElement(parent_node, ns["cac"] + "PartyTaxScheme")
            registration_name = etree.SubElement(party_tax_scheme, ns["cbc"] + "RegistrationName")
            registration_name.text = commercial_partner.name
            company_id = etree.SubElement(party_tax_scheme, ns["cbc"] + "CompanyID")
            company_id.text = commercial_partner.vat
            tax_scheme_dict = self._fe_cr_get_tax_scheme_dict_from_partner(commercial_partner)
            self._fe_cr_add_tax_scheme(tax_scheme_dict, party_tax_scheme, ns, version=version)

    @api.model
    def _fe_cr_add_party_legal_entity(self, commercial_partner, parent_node, ns, version="2.1"):
        party_legal_entity = etree.SubElement(parent_node, ns["cac"] + "PartyLegalEntity")
        registration_name = etree.SubElement(party_legal_entity, ns["cbc"] + "RegistrationName")
        registration_name.text = commercial_partner.name
        self._fe_cr_add_address(
            commercial_partner, "RegistrationAddress", party_legal_entity, ns, version=version
        )

    @api.model
    def _fe_cr_add_party(self, partner, company, node_name, parent_node, ns, version="2.1"):
        commercial_partner = partner.commercial_partner_id
        party = etree.SubElement(parent_node, ns["cac"] + node_name)
        if commercial_partner.website:
            website = etree.SubElement(party, ns["cbc"] + "WebsiteURI")
            website.text = commercial_partner.website
        self._fe_cr_add_party_identification(commercial_partner, party, ns, version=version)
        party_name = etree.SubElement(party, ns["cac"] + "PartyName")
        name = etree.SubElement(party_name, ns["cbc"] + "Name")
        name.text = commercial_partner.name
        if partner.lang:
            self._fe_cr_add_language(partner.lang, party, ns, version=version)
        self._fe_cr_add_address(commercial_partner, "PostalAddress", party, ns, version=version)
        self._fe_cr_add_party_tax_scheme(commercial_partner, party, ns, version=version)
        if company:
            self._fe_cr_add_party_legal_entity(commercial_partner, party, ns, version="2.1")
        self._fe_cr_add_contact(partner, party, ns, version=version)

    @api.model
    def _fe_cr_add_customer_party(
        self, partner, company, node_name, parent_node, ns, version="2.1"
    ):
        if company:
            if partner:
                assert partner.commercial_partner_id == company.partner_id, "partner is wrong"
            else:
                partner = company.partner_id
        customer_party_root = etree.SubElement(parent_node, ns["cac"] + node_name)
        if not company and partner.commercial_partner_id.ref:
            customer_ref = etree.SubElement(
                customer_party_root, ns["cbc"] + "SupplierAssignedAccountID"
            )
            customer_ref.text = partner.commercial_partner_id.ref
        self._fe_cr_add_party(partner, company, "Party", customer_party_root, ns, version=version)
        # TODO: rewrite support for AccountingContact + add DeliveryContact
        # Additionnal optional args
        if partner and not company and partner.parent_id:
            self._fe_cr_add_contact(
                partner, customer_party_root, ns, node_name="AccountingContact", version=version
            )

    @api.model
    def _fe_cr_add_supplier_party(
        self, partner, company, node_name, parent_node, ns, version="2.1"
    ):
        if company:
            if partner:
                assert partner.commercial_partner_id == company.partner_id, "partner is wrong"
            else:
                partner = company.partner_id
        supplier_party_root = etree.SubElement(parent_node, ns["cac"] + node_name)
        if not company and partner.commercial_partner_id.ref:
            supplier_ref = etree.SubElement(
                supplier_party_root, ns["cbc"] + "CustomerAssignedAccountID"
            )
            supplier_ref.text = partner.commercial_partner_id.ref
        self._fe_cr_add_party(partner, company, "Party", supplier_party_root, ns, version=version)

    @api.model
    def _fe_cr_add_delivery(self, delivery_partner, parent_node, ns, version="2.1"):
        delivery = etree.SubElement(parent_node, ns["cac"] + "Delivery")
        delivery_location = etree.SubElement(delivery, ns["cac"] + "DeliveryLocation")
        self._fe_cr_add_address(delivery_partner, "Address", delivery_location, ns, version=version)
        self._fe_cr_add_party(
            delivery_partner, False, "DeliveryParty", delivery, ns, version=version
        )

    @api.model
    def _fe_cr_add_delivery_terms(self, incoterm, parent_node, ns, version="2.1"):
        delivery_term = etree.SubElement(parent_node, ns["cac"] + "DeliveryTerms")
        delivery_term_id = etree.SubElement(
            delivery_term, ns["cbc"] + "ID", schemeAgencyID="6", schemeID="INCOTERM"
        )
        delivery_term_id.text = incoterm.code

    @api.model
    def _fe_cr_add_payment_terms(self, payment_term, parent_node, ns, version="2.1"):
        pay_term_root = etree.SubElement(parent_node, ns["cac"] + "PaymentTerms")
        pay_term_note = etree.SubElement(pay_term_root, ns["cbc"] + "Note")
        pay_term_note.text = payment_term.name

    @api.model
    def _fe_cr_add_tax_subtotal(
        self, taxable_amount, tax_amount, tax, currency_code, parent_node, ns, version="2.1"
    ):
        prec = self.env["decimal.precision"].precision_get("Account")
        tax_subtotal = etree.SubElement(parent_node, ns["cac"] + "TaxSubtotal")
        if not float_is_zero(taxable_amount, precision_digits=prec):
            taxable_amount_node = etree.SubElement(
                tax_subtotal, ns["cbc"] + "TaxableAmount", currencyID=currency_code
            )
            taxable_amount_node.text = "%0.*f" % (prec, taxable_amount)
        tax_amount_node = etree.SubElement(
            tax_subtotal, ns["cbc"] + "TaxAmount", currencyID=currency_code
        )
        tax_amount_node.text = "%0.*f" % (prec, tax_amount)
        if tax.amount_type == "percent" and not float_is_zero(
            tax.amount, precision_digits=prec + 3
        ):
            percent = etree.SubElement(tax_subtotal, ns["cbc"] + "Percent")
            percent.text = str(float_round(tax.amount, precision_digits=2))
        self._fe_cr_add_tax_category(tax, tax_subtotal, ns, version=version)

    @api.model
    def _fe_cr_add_tax_category(self, tax, parent_node, ns, node_name="TaxCategory", version="2.1"):
        tax_category = etree.SubElement(parent_node, ns["cac"] + node_name)
        if not tax.unece_categ_id:
            raise UserError(_("Missing UNECE Tax Category on tax '{}'").format(tax.name))
        tax_category_id = etree.SubElement(
            tax_category, ns["cbc"] + "ID", schemeID="UN/ECE 5305", schemeAgencyID="6"
        )
        tax_category_id.text = tax.unece_categ_code
        tax_name = etree.SubElement(tax_category, ns["cbc"] + "Name")
        tax_name.text = tax.name
        if tax.amount_type == "percent":
            tax_percent = etree.SubElement(tax_category, ns["cbc"] + "Percent")
            tax_percent.text = str(tax.amount)
        tax_scheme_dict = self._fe_cr_get_tax_scheme_dict_from_tax(tax)
        self._fe_cr_add_tax_scheme(tax_scheme_dict, tax_category, ns, version=version)

    @api.model
    def _fe_cr_get_tax_scheme_dict_from_tax(self, tax):
        if not tax.unece_type_id:
            raise UserError(_("Missing UNECE Tax Type on tax '{}'").format(tax.name))
        tax_scheme_dict = {
            "id": tax.unece_type_code,
            "name": False,
            "type_code": False,
        }
        return tax_scheme_dict

    @api.model
    def _fe_cr_add_tax_scheme(self, tax_scheme_dict, parent_node, ns, version="2.1"):
        tax_scheme = etree.SubElement(parent_node, ns["cac"] + "TaxScheme")
        if tax_scheme_dict.get("id"):
            tax_scheme_id = etree.SubElement(
                tax_scheme, ns["cbc"] + "ID", schemeID="UN/ECE 5153", schemeAgencyID="6"
            )
            tax_scheme_id.text = tax_scheme_dict["id"]
        if tax_scheme_dict.get("name"):
            tax_scheme_name = etree.SubElement(tax_scheme, ns["cbc"] + "Name")
            tax_scheme_name.text = tax_scheme_dict["name"]
        if tax_scheme_dict.get("type_code"):
            tax_scheme_type_code = etree.SubElement(tax_scheme, ns["cbc"] + "TaxTypeCode")
            tax_scheme_type_code.text = tax_scheme_dict["type_code"]

    @api.model
    def _fe_cr_get_nsmap_namespace(self, doc_name, version="2.1"):
        nsmap = {
            None: "urn:oasis:names:specification:fe_cr:schema:xsd:" + doc_name,
            "cac": "urn:oasis:names:specification:fe_cr:" "schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:fe_cr:schema:xsd:" "CommonBasicComponents-2",
        }
        ns = {
            "cac": "{urn:oasis:names:specification:fe_cr:schema:xsd:"
            "CommonAggregateComponents-2}",
            "cbc": "{urn:oasis:names:specification:fe_cr:schema:xsd:" "CommonBasicComponents-2}",
        }
        return nsmap, ns

    @api.model
    def _fe_cr_check_xml_schema(self, xml_string, document, version="2.1"):
        """Validate the XML file against the XSD"""
        xsd_filename = "/opt/ambientes/Odoo10/MyAddons/base_fe_cr/data/xsd-{}/{}_V{}.xsd".format(
            version, document, version
        )

        with open(xsd_filename, "r") as xsd_file:
            schema_to_check = xsd_file.read()

        xsd_etree_obj = etree.parse(StringIO(schema_to_check))
        official_schema = etree.XMLSchema(xsd_etree_obj)
        try:
            t = etree.parse(StringIO(xml_string))
            official_schema.assertValid(t)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning("The XML file is invalid against the XML Schema Definition")
            logger.warning(xml_string)
            logger.warning(e)
            raise UserError(
                _(
                    "The UBL XML file is not valid against the official "
                    "XML Schema Definition. The XML file and the "
                    "full error have been written in the server logs. "
                    "Here is the error, which may give you an idea on the "
                    "cause of the problem : {}."
                ).format(str(e))
            )

        return True

    @api.model
    def embed_xml_in_pdf(self, xml_string, xml_filename, pdf_content=None, pdf_file=None):
        assert pdf_content or pdf_file, "Missing pdf_file or pdf_content"
        logger.debug("Starting to embed {} in PDF file".format(xml_filename))
        if pdf_file:
            original_pdf_file = pdf_file
        elif pdf_content:
            original_pdf_file = StringIO(pdf_content)
        original_pdf = PdfFileReader(original_pdf_file)
        new_pdf_filestream = PdfFileWriter()
        new_pdf_filestream.appendPagesFromReader(original_pdf)
        new_pdf_filestream.addAttachment(xml_filename, xml_string)
        new_pdf_filestream._root_object.update(
            {
                NameObject("/PageMode"): NameObject("/UseAttachments"),
            }
        )
        if pdf_file:
            f = open(pdf_file, "wb")
            new_pdf_filestream.write(f)
            f.close()
        elif pdf_content:
            with NamedTemporaryFile(prefix="odoo-fe_cr-", suffix=".pdf") as f:
                new_pdf_filestream.write(f)
                f.seek(0)
                pdf_content = f.read()
                f.close()
        logger.info("{} file added to PDF".format(xml_filename))
        return pdf_content

    # ==================== METHODS TO PARSE UBL files

    @api.model
    def fe_cr_parse_customer_party(self, customer_party_node, ns):
        ref_xpath = customer_party_node.xpath("cac:SupplierAssignedAccountID", namespaces=ns)
        party_node = customer_party_node.xpath("cac:Party", namespaces=ns)[0]
        partner_dict = self.fe_cr_parse_party(party_node, ns)
        partner_dict["ref"] = ref_xpath and ref_xpath[0].text or False
        return partner_dict

    @api.model
    def fe_cr_parse_supplier_party(self, customer_party_node, ns):
        ref_xpath = customer_party_node.xpath("cac:CustomerAssignedAccountID", namespaces=ns)
        party_node = customer_party_node.xpath("cac:Party", namespaces=ns)[0]
        partner_dict = self.fe_cr_parse_party(party_node, ns)
        partner_dict["ref"] = ref_xpath and ref_xpath[0].text or False
        return partner_dict

    @api.model
    def fe_cr_parse_party(self, party_node, ns):
        partner_vat = party_node.find("inv:Identificacion/inv:Numero", ns).text
        partner = self.env["res.partner"].search([("vat", "=", partner_vat)])
        if partner:
            partner_dict = {
                "vat": partner_vat,
                "name": partner.name,
                "email": partner.email,
                "phone": partner.phone,
            }
        else:
            name = party_node.xpath("inv:Nombre", namespaces=ns)
            email = party_node.xpath("inv:CorreoElectronico", namespaces=ns)
            phone = party_node.xpath("inv:Telefono/inv:NumTelefono", namespaces=ns)
            partner_dict = {
                "vat": partner_vat,
                "name": name[0].text,
                "email": email and email[0].text or "",
                "phone": phone and phone[0].text or "",
            }

        address_xpath = party_node.find("inv:Ubicacion", namespaces=ns)
        if address_xpath is not None:
            address_dict = self.fe_cr_parse_address(address_xpath, ns)
            partner_dict.update(address_dict)
        return partner_dict

    @api.model
    def fe_cr_parse_address(self, address_node, ns):
        country_code = "CR"

        state_code_xpath = address_node.xpath("inv:Provincia", namespaces=ns)
        state_code = state_code_xpath and state_code_xpath[0].text or False

        county_code_xpath = address_node.xpath("inv:Canton", namespaces=ns)
        county_code = county_code_xpath and county_code_xpath[0].text or False

        district_code_xpath = address_node.xpath("inv:Distrito", namespaces=ns)
        district_code = district_code_xpath and district_code_xpath[0].text or False

        address_dict = {
            "country_code": country_code,
            "state_code": state_code,
            "county_code": county_code,
            "district_code": district_code,
        }
        return address_dict

    @api.model
    def fe_cr_parse_delivery(self, delivery_node, ns):
        party_xpath = delivery_node.xpath("cac:DeliveryParty", namespaces=ns)
        if party_xpath:
            partner_dict = self.fe_cr_parse_party(party_xpath[0], ns)
        else:
            partner_dict = {}
        delivery_address_xpath = delivery_node.xpath(
            "cac:DeliveryLocation/cac:Address", namespaces=ns
        )
        if not delivery_address_xpath:
            delivery_address_xpath = delivery_node.xpath("cac:DeliveryAddress", namespaces=ns)
        if delivery_address_xpath:
            address_dict = self.fe_cr_parse_address(delivery_address_xpath[0], ns)
        else:
            address_dict = {}
        delivery_dict = {
            "partner": partner_dict,
            "address": address_dict,
        }
        return delivery_dict

    def fe_cr_parse_incoterm(self, delivery_term_node, ns):
        incoterm_xpath = delivery_term_node.xpath("cbc:ID", namespaces=ns)
        if incoterm_xpath:
            incoterm_dict = {"code": incoterm_xpath[0].text}
            return incoterm_dict
        return {}

    def fe_cr_parse_product(self, line_node, ns):
        barcode_xpath = line_node.xpath(
            "cac:Item/cac:StandardItemIdentification/cbc:ID[@schemeID='GTIN']", namespaces=ns
        )
        code_xpath = line_node.xpath("cac:Item/cac:SellersItemIdentification/cbc:ID", namespaces=ns)
        product_dict = {
            "barcode": barcode_xpath and barcode_xpath[0].text or False,
            "code": code_xpath and code_xpath[0].text or False,
        }
        return product_dict

    def get_xml_files_from_pdf(self, pdf_file):
        logger.info("Trying to find an embedded XML file inside PDF")
        res = {}
        try:
            fd = StringIO(pdf_file)
            pdf = PdfFileReader(fd)
            logger.debug("pdf.trailer={}".format(pdf.trailer))
            pdf_root = pdf.trailer["/Root"]
            logger.debug("pdf_root={}".format(pdf_root))
            embeddedfiles = pdf_root["/Names"]["/EmbeddedFiles"]["/Names"]
            i = 0
            xmlfiles = {}
            for embeddedfile in embeddedfiles[:-1]:
                mime_res = mimetypes.guess_type(embeddedfile)
                if mime_res and mime_res[0] in ["application/xml", "text/xml"]:
                    xmlfiles[embeddedfile] = embeddedfiles[i + 1]
                i += 1
            logger.debug("xmlfiles={}".format(xmlfiles))
            for filename, xml_file_dict_obj in xmlfiles.items():
                try:
                    xml_file_dict = xml_file_dict_obj.getObject()
                    logger.debug("xml_file_dict={}".format(xml_file_dict))
                    xml_string = xml_file_dict["/EF"]["/F"].getData()
                    xml_root = etree.fromstring(xml_string)
                    logger.debug(
                        "A valid XML file {} has been found in the PDF file".format(filename)
                    )
                    res[filename] = xml_root
                except:
                    continue
        except:
            pass
        logger.info("Valid XML files found in PDF: {}".format(list(res.keys())))
        return res
