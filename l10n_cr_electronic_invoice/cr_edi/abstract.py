class Document:
    TYPE_TO_CODE = {
        "FE": "01",
        "ND": "02",
        "NC": "03",
        "TE": "04",
        "CCE": "05",
        "CPCE": "06",
        "RCE": "07",
        "FEC": "08",
        "FEE": "09",
    }


class Voucher:
    TYPE_TO_CODE = {
        "normal": "1",
        "contingencia": "2",
        "sininternet": "3",
    }


class Sequence:
    @staticmethod
    def valid(sequence):
        return sequence.isdigit() and len(sequence) == 10


class Environment:
    class STAGING:
        client_id = "api-stag"
        token_endpoint = "https://idp.comprobanteselectronicos.go.cr/auth/realms/rut-stag/protocol/openid-connect/token"
        reception_endpoint = (
            "https://api.comprobanteselectronicos.go.cr/recepcion-sandbox/v1/recepcion"
        )

    class PRODUCTION:
        client_id = "api-prod"
        token_endpoint = "https://idp.comprobanteselectronicos.go.cr/auth/realms/rut/protocol/openid-connect/token"
        reception_endpoint = "https://api.comprobanteselectronicos.go.cr/recepcion/v1/recepcion"

    _client_id_to_class = {
        "api-stag": STAGING,
        "api-prod": PRODUCTION,
    }

    @staticmethod
    def get(client_id):
        return Environment._client_id_to_class[client_id]
