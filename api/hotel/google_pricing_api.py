from typing import Union, List

from lxml import etree

from api import logger
from api.common.common_models import SimplenightModel
from api.models.models import ProviderHotel


class GooglePricingItineraryQuery(SimplenightModel):
    checkin: str
    nights: int
    hotel_codes: List[str]


def parse_request(xmlstr: Union[str, bytes]):
    if isinstance(xmlstr, str):
        xmlstr = xmlstr.encode("utf-8")

    parser = etree.XMLParser(recover=True, encoding="utf-8")
    doc = etree.fromstring(xmlstr, parser)

    return GooglePricingItineraryQuery(
        checkin=doc.find("Checkin").text,
        nights=int(doc.find("Nights").text),
        hotel_codes=list(map(lambda x: x.text, doc.findall("PropertyList/Property"))),
    )


def generate_property_list(country_codes: str, provider_name="giata"):
    country_codes = country_codes.split(",")
    logger.info(f"Searching for hotels in {country_codes}")

    provider_hotels = ProviderHotel.objects.filter(provider__name=provider_name, country_code__in=country_codes)
    logger.info(f"Found {len(provider_hotels)} hotels")

    root = etree.Element("listings")
    root.append(_get_element("language", "en"))

    for provider_hotel in provider_hotels:
        listing = etree.Element("listing")
        listing.append(_get_element("id", provider_hotel.provider_code))
        listing.append(_get_element("name", provider_hotel.hotel_name))

        address = etree.Element("address")
        address.attrib["format"] = "simple"
        address.append(_get_element("component", provider_hotel.address_line_1, name="addr1"))
        address.append(_get_element("component", provider_hotel.city_name, name="city"))
        address.append(_get_element("component", provider_hotel.country_code, name="country"))
        address.append(_get_element("component", provider_hotel.postal_code, name="postal_code"))
        address.append(_get_element("component", provider_hotel.state, name="state"))
        listing.append(address)

        listing.append(_get_element("country", provider_hotel.country_code))
        listing.append(_get_element("latitude", str(provider_hotel.latitude), cdata=False))
        listing.append(_get_element("longitude", str(provider_hotel.longitude), cdata=False))
        listing.append(_get_element("phone", "", type="main"))

        root.append(listing)

    return etree.tostring(root)


def _get_element(tag, content, cdata=True, **attribs):
    element = etree.Element(tag)
    if content:
        if cdata:
            element.text = etree.CDATA(content)
        else:
            element.text = content

    for key, value in attribs.items():
        element.attrib[key] = value

    return element
