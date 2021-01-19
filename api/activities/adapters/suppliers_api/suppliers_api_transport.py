import abc
from enum import Enum

import requests

from api import logger
from api.hotel.adapters.transport import Transport


class SuppliersApiTransport(Transport, abc.ABC):
    def __init__(self, test_mode=True):
        super().__init__()
        self.test_mode = test_mode

    class Endpoint(Enum):
        SEARCH = "search"

    def _get_headers(self, **kwargs):
        return {
            "Content-Type": "application/json",
        }

    def search(self, **data):
        return self.post(self.Endpoint.SEARCH, **data)

    def post(self, endpoint: Endpoint, **params):
        url = self.get_endpoint(endpoint)

        logger.info(f"Making request to {url}")
        logger.debug(f"Params: {params}")

        response = requests.post(url, json=params, headers=self._get_headers())
        logger.info(f"Request complete to {url}")

        if not response.ok:
            logger.error(f"Error while searching Priceline: {response.text}")

        return response.json()

    @staticmethod
    @abc.abstractmethod
    def get_supplier_name():
        pass

    @classmethod
    def get_endpoint(cls, endpoint: Endpoint):
        return f"https://suppliers-api.qa-new.simplenight.com/v1/{cls.get_supplier_name()}/{endpoint.value}"
