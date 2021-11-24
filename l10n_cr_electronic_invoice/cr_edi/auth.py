from datetime import datetime, timedelta

import requests

from . import abstract


class Token:
    access_token = None
    expires = None

    def __init__(self, username: str, password: str, environment: abstract.Environment):
        """Create a Token object with their value and expiration date

        Args:
            username (str): Username to make connection
            password (str): Password to mane connection
            environment (Environment): Environment to get client_id and token_endpoint
        """
        response_json = Token._get_new_token(username, password, environment)
        self.access_token = response_json["access_token"]
        self.expires = datetime.now() + timedelta(seconds=response_json["expires_in"])

    @staticmethod
    def _get_new_token(username: str, password: str, environment: str) -> dict:
        """Gets new token value from external API

        Args:
            username (str): Username
            password (str): Password
            environment (Environment): [description]

        Raises:
            Exception: If API response is not satisfactory

        Returns:
            dict: API response in JSON
        """
        headers = {}
        data = {
            "client_secret": "",
            "grant_type": "password",
            "client_id": environment.client_id,
            "username": username,
            "password": password,
        }
        response = requests.post(environment.token_endpoint, data=data, headers=headers)
        response_json = response.json()
        if 200 <= response.status_code <= 299:
            return response_json
        else:
            raise Exception(response.status_code, response.reason)

    def is_valid(self):
        """Validate the expiration date is in the future

        Returns:
            bool: Returns True if the code is still valid
        """
        now = datetime.now()
        return self.expires > now


tokens = {}


def get_token(internal_id: int, username: str, password: str, client_id: str):
    """Get valid token value

    Args:
        internal_id (int): ID used to keep multiple token context at the same time (usually Issuer identifier)
        username (str): Username
        password (str): Password
        client_id (str): client_id to be use in Endpoint.get function, (stag or production)

    Returns:
        str: Valid access token
    """
    global tokens
    environment = abstract.Environment.get(client_id)
    token = tokens.get(internal_id)
    if not token or not token.is_valid():
        token = Token(
            username=username,
            password=password,
            environment=environment,
        )
        tokens[id] = token
    return token.access_token
