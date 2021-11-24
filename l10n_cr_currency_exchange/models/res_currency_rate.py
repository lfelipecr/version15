import logging
from datetime import datetime

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)

# TODO Analyze if EUR necessary
CRC_USD_RATE_API = "https://api.hacienda.go.cr/indicadores/tc/dolar"


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    @api.model
    def update_crc_usd_rate(self):
        crc_currency = self.env.ref("base.CRC")
        usd_currency = self.env.ref("base.USD")
        for company in self.env["res.company"].search([]):
            if company.currency_id != crc_currency:
                continue
            _logger.info("Executing exchange rate update on company {}".format(company.name))

            response = requests.get(CRC_USD_RATE_API)
            if response.status_code != 200:
                _logger.error("Error in the CRC/USD rate API call")
                return
            response_json = response.json()
            now = datetime.now().date()  # TODO ensure is UTC and no CR local
            current_rate = self.search(
                [
                    ("company_id", "=", company.id),
                    ("currency_id", "=", usd_currency.id),
                    ("name", "=", now),
                ],
                limit=1,
            )
            usd_to_crc = response_json["venta"]["valor"]
            crc_to_usd = 1 / usd_to_crc
            if current_rate:
                current_rate.rate = crc_to_usd
            else:
                self.create(
                    {
                        "company_id": company.id,
                        "currency_id": usd_currency.id,
                        "name": now,
                        "rate": crc_to_usd,
                    }
                )
