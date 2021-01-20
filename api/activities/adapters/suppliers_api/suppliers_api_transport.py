import abc
import urllib.parse
from datetime import date
from enum import Enum
from typing import Dict

import requests

from api import logger
from api.hotel.adapters.transport import Transport


class SuppliersApiTransport(Transport, abc.ABC):
    def __init__(self, test_mode=True):
        super().__init__()
        self.test_mode = test_mode

    class Endpoint(Enum):
        SEARCH = "search"
        DETAILS = "details"
        BOOK = "book"
        CANCEL = "cancel"

    def _get_headers(self, **kwargs):
        return {
            "Content-Type": "application/json",
        }

    def search(self, **data):
        return self.post(self.Endpoint.SEARCH, **data)

    def details(self, date_from: date = None, date_to: date = None, **data):
        query_params = {}
        if date_from or date_to:
            query_params["date_from"] = date_from
            query_params["date_to"] = date_to

        return self.post(self.Endpoint.DETAILS, query_params, **data)

    def book(self, **data):
        return self.post(self.Endpoint.BOOK, **data)

    def cancel(self, **data):
        return self.post(self.Endpoint.CANCEL, **data)

    def post(self, endpoint: Endpoint, query_params: Dict = None, **params):
        url = self.get_endpoint(endpoint,)

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
    def get_endpoint(cls, endpoint: Endpoint, params: Dict = None):
        base_url = f"https://suppliers-api.qa-new.simplenight.com/v1/{cls.get_supplier_name()}/{endpoint.value}"
        if not params:
            return base_url

        return base_url + urllib.parse.urlencode(params)
