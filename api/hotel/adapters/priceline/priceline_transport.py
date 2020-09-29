from enum import Enum

import requests

from api import logger
from api.hotel.adapters.transport import Transport


class PricelineTransport(Transport):
    class Endpoint(Enum):
        HOTEL_EXPRESS = "/hotel/getExpress.Results"
        HOTEL_DETAILS = "/hotel/getHotelDetails"
        EXPRESS_BOOK = "/hotel/getExpress.Book"
        EXPRESS_CONTRACT = "/hotel/getExpress.Contract"
        HOTELS_DOWNLOAD = "/shared/getBOF2.Downloads.Hotel.Hotels"
        PHOTOS_DOWNLOAD = "/shared/getBOF2.Downloads.Hotel.Photos"

    CREDENTIALS = {
        "refid": "10046",
        "api_key": "990b98b0a0efaa7acf461ff6a60cf726",
    }

    def __init__(self, test_mode=True):
        super().__init__()
        self.test_mode = test_mode

    def get(self, endpoint: Endpoint, **params):
        url = self.endpoint(endpoint)
        params.update(self._get_default_params())

        logger.info(f"Making request to {url}")

        response = requests.get(url, params=params, headers=self._get_headers())
        if not response.ok:
            logger.error(f"Error while searching Priceline: {response.text}")

        return response.json()

    def post(self, endpoint: Endpoint, **params):
        url = self.endpoint(endpoint)
        params.update(self._get_default_params())

        logger.info(f"Making request to {url}")

        response = requests.post(url, data=params, headers=self._get_headers())
        if not response.ok:
            logger.error(f"Error while searching Priceline: {response.text}")

        return response.json()

    def hotel_express(self, **params):
        return self.get(self.Endpoint.HOTEL_EXPRESS, **params)

    def hotel_details(self, **params):
        return self.get(self.Endpoint.HOTEL_DETAILS, **params)

    def express_book(self, **params):
        return self.post(self.Endpoint.EXPRESS_BOOK, **params)

    def express_contract(self, **params):
        return self.post(self.Endpoint.EXPRESS_CONTRACT, **params)

    def hotels_download(self, **params):
        return self.get(self.Endpoint.HOTELS_DOWNLOAD, **params)

    def photos_download(self, **params):
        return self.get(self.Endpoint.PHOTOS_DOWNLOAD, **params)

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
