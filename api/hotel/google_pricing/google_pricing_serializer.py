import uuid
from datetime import date, datetime
from typing import Union, List

from lxml import etree

from api.hotel.google_pricing.google_pricing_models import GooglePricingItineraryQuery
from api.hotel.models.hotel_api_model import SimplenightHotel


def deserialize(xmlstr: Union[str, bytes]) -> GooglePricingItineraryQuery:
    if isinstance(xmlstr, str):
        xmlstr = xmlstr.encode("utf-8")

    parser = etree.XMLParser(recover=True, encoding="utf-8")
    doc = etree.fromstring(xmlstr, parser)

    return GooglePricingItineraryQuery(
        checkin=date.fromisoformat(doc.find("Checkin").text),
        nights=int(doc.find("Nights").text),
        hotel_codes=list(map(lambda x: x.text, doc.findall("PropertyList/Property"))),
    )


def serialize(query: GooglePricingItineraryQuery, hotels: List[SimplenightHotel]) -> str:
    transaction = etree.Element("Transaction")
    transaction.attrib["timestamp"] = str(datetime.now())
    transaction.attrib["id"] = str(uuid.uuid4())

    for hotel in hotels:
        result = etree.Element("Result")
        result.append(_get_element("Property", hotel.hotel_id))
        result.append(_get_element("Checkin", str(hotel.start_date), cdata=False))
        result.append(_get_element("Nights", str(query.nights), cdata=False))

        lowest_rate_room = min(hotel.room_types, key=lambda x: x.total.amount)
        result.append(_get_element("RoomID", "lowest_rate"))

        base_rate = etree.Element("Baserate")
        base_rate.attrib["currency"] = lowest_rate_room.total.currency
        base_rate.attrib["all_inclusive"] = "false"
        base_rate.text = str(lowest_rate_room.total.amount)
        result.append(base_rate)

        tax = etree.Element("Tax")
        tax.attrib["currency"] = lowest_rate_room.total.currency
        tax.text = str(lowest_rate_room.total_tax_rate.amount)
        result.append(tax)

        other_fees = etree.Element("OtherFees")
        other_fees.attrib["currency"] = lowest_rate_room.total.currency
        other_fees.text = "0"
        result.append(other_fees)
        if lowest_rate_room.postpaid_fees:
            other_fees.text = str(lowest_rate_room.postpaid_fees.total.amount)

        transaction.append(result)

    return etree.tostring(transaction)


# <?xml version="1.0" encoding="UTF-8"?>
# <Transaction timestamp="2020-11-10T01:03:40+00:00" id="1ff18df8-7153-4388-a99b-77005db8039d">
#   <Result>
#     <Property><![CDATA[MX-58244]]></Property>
#     <Checkin>2020-12-29</Checkin>
#     <Nights>1</Nights>
#     <RoomID><![CDATA[lowest_rate]]></RoomID>
#     <Baserate currency="USD" all_inclusive="false">73.99</Baserate>
#     <Tax currency="USD">6.07</Tax>
#     <OtherFees currency="USD">0</OtherFees>

def serialize_property_list(provider_hotels):
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
        content = content.strip()
        if cdata:
            element.text = etree.CDATA(content)
        else:
            element.text = content

    for key, value in attribs.items():
        element.attrib[key] = value

    return element
