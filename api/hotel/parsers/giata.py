import aiohttp
import requests
from lxml import etree
from requests.auth import HTTPBasicAuth

from api import logger
from api.models.models import Provider, ProviderHotel, ProviderMapping


class GiataParser:
    _MULTI_CODE_URL = "https://multicodes.giatamedia.com/webservice/rest/1.0/properties/multi"
    _USERNAME = "justin|simplenight.com"
    _PASSWORD = "Developers!23"

    def __init__(self):
        self.auth = HTTPBasicAuth(self._USERNAME, self._PASSWORD)
        self.provider, created = Provider.objects.get_or_create(name="giata")
        self.provider_map = self.get_provider_map()

    def get_properties(self, pagination_link=None):
        endpoint = self._get_endpoint(pagination_link)
        response = requests.get(endpoint, auth=self.auth)
        if response.ok:
            return response.content

    @staticmethod
    def get_provider_map():
        return {
            "priceline_partner_network": Provider.objects.get_or_create(name="priceline")[0],
            "iceportal": Provider.objects.get_or_create(name="iceportal")[0],
        }

    def execute(self):
        pagination_link = ""
        while pagination_link is not None:
            properties_xmlstr = self.get_properties(pagination_link=pagination_link)
            pagination_link = self.parse_properties(properties_xmlstr)

    def parse_properties(self, properties_xmlstr):
        parser = etree.XMLParser(recover=True, encoding="utf-8")
        doc = etree.fromstring(properties_xmlstr, parser)
        namespaces = {"xlink": "http://www.w3.org/1999/xlink"}
        pagination_link = doc.xpath("./more/@xlink:href", namespaces=namespaces)
        if len(pagination_link) > 0:
            pagination_link = pagination_link[0]
            logger.info("Next URL: " + pagination_link)

        provider_hotels = []
        provider_mappings = []
        for element in doc.findall(".//property"):
            giata_id = element.get("giataId")
            hotel_name = self._find_with_default(element, "name")
            city_name = self._find_with_default(element, "addresses/address[1]/cityName")
            country = self._find_with_default(element, "addresses/address[1]/country")
            postal_code = self._find_with_default(element, "addresses/address[1]/postalCode")
            address_line_1 = self._find_with_default(element, "addresses/address[1]/addressLine[@addressLineNumber]")
            address_line_2 = self._find_with_default(element, "addresses/address[1]/addressLine[@addressLineNumber]")
            latitude = self._find_with_default(element, "geoCodes/geoCode/latitude")
            longitude = self._find_with_default(element, "geoCodes/geoCode/longitude")

            model = ProviderHotel(
                provider=self.provider,
                provider_code=giata_id,
                hotel_name=hotel_name,
                city_name=city_name,
                country_code=country,
                postal_code=postal_code,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                latitude=latitude,
                longitude=longitude
            )

            provider_hotels.append(model)

            provider_codes = element.find("propertyCodes")
            if provider_codes is None:
                continue

            for provider_code in provider_codes:
                provider_name = provider_code.get("providerCode")
                property_code = self._find_with_default(provider_code, "code/value")
                if provider_name not in self.provider_map:
                    continue

                mapping = ProviderMapping(
                    provider=self.provider_map[provider_name],
                    giata_code=giata_id,
                    provider_code=property_code
                )

                provider_mappings.append(mapping)

        try:
            ProviderHotel.objects.bulk_create(provider_hotels)
            ProviderMapping.objects.bulk_create(provider_mappings)
        except Exception:
            logger.exception("Error persisting models to DB")

        return pagination_link

    def _get_endpoint(self, pagination_link):
        if not pagination_link:
            return self._MULTI_CODE_URL

        return pagination_link

    @staticmethod
    def _find_with_default(element, xpath, default=None):
        child = element.find(xpath)
        if child is not None:
            return child.text

        return default

