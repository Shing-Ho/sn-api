from enum import Enum

import requests

from api import logger
from api.hotel.adapters.transport import Transport


class PricelineTransport(Transport):
    class Endpoint(Enum):
        HOTEL_EXPRESS = "/hotel/getExpress.Results"
        HOTEL_DETAILS = "/hotel/getHotelDetails"

    CREDENTIALS = {
        "refid": "10045",
        "api_key": "990b98b0a0efaa7acf461ff6a60cf726",
    }

    def __init__(self, test_mode=True):
        super().__init__()
        self.test_mode = test_mode

    def get(self, endpoint: Endpoint, **params):
        url = self.endpoint(endpoint)
        params.update(self._get_default_params())

        logger.info(f"Making request to {url}")

        return requests.get(url, params=params, headers=self._get_headers())

    def hotel_express(self, **params):
        return self.get(self.Endpoint.HOTEL_EXPRESS, **params)

    def hotel_details(self, **params):
        return self.get(self.Endpoint.HOTEL_DETAILS, **params)

    def endpoint(self, priceline_endpoint: Endpoint):
        return f"{self._get_host()}{priceline_endpoint.value}"

    def _get_headers(self, **kwargs):
        headers = self._get_default_headers()
        headers.update(kwargs)

        return headers

    def _get_default_params(self):
        return {**self.CREDENTIALS, "format": "json2"}

    def _get_host(self):
        if not self.test_mode:
            return "https://api.rezserver.com/api"

        return "https://api-sandbox.rezserver.com/api"
