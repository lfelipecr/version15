import re

import requests

from odoo import _, api, models
from odoo.exceptions import UserError

NIF_API = "https://api.hacienda.go.cr/fe/ae"


class Partner(models.Model):
    _inherit = "res.partner"

    @api.onchange("vat", "identification_id")
    def _verify_vat_and_identification_id(self):  # TODO in res.company
        if not (self.identification_id and self.vat):
            return
        self.vat = re.sub(r"[^\d]", "", self.vat)
        lens = {
            "01": (9, 9),
            "02": (10, 10),
            "03": (11, 12),
            "04": (9, 9),
            "05": (20, 20),
        }
        limits = lens[self.identification_id.code]
        if not limits[0] <= len(self.vat) <= limits[1]:
            raise UserError(
                _("VAT must be between {} and {} (inclusive) chars long").format(
                    limits[0],
                    limits[1],
                )
            )

    @api.onchange("vat")
    def _get_name_from_vat(self):
        if not self.vat:
            return
        response = requests.get(NIF_API, params={"identificacion": self.vat})
        if response.status_code == 200:
            response_json = response.json()
            self.name = response_json["nombre"]
            self.identification_id = self.identification_id.search(
                [("code", "=", response_json["tipoIdentificacion"])], limit=1
            )
            return
        elif response.status_code == 404:
            title = "VAT Not found"
            message = "The VAT is not on the API"
        elif response.status_code == 400:
            title = "API Error 400"
            message = "Bad Request"
        else:
            title = "Unknown Error"
            message = "Unknown error in the API request"
        return {
            "warning": {
                "title": title,
                "message": message,
            }
        }
