from datetime import date, timedelta
from typing import List, Optional

from api.hotel.adapters.travelport.hotel_details import TravelportHotelDetailsBuilder
from api.hotel.adapters.travelport.search import TravelportHotelSearchBuilder
from api.hotel.adapters.travelport.transport import TravelportTransport
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotels import (
    HotelLocationSearch,
    HotelAdapterHotel,
    Address,
    HotelRate,
    HotelDetailsSearchRequest,
    HotelDetails,
    Money,
    DailyRate,
    RoomRate,
    HotelSpecificSearch,
    HotelSearchResponseHotel,
    GeoLocation,
    HotelBookingRequest,
)

secrets = {
    "url": "https://americas.universal-api.travelport.com/B2BGateway/connect/uAPI/HotelService",
    "username": "Universal API/uAPI9027118295-d926ccdb",
    "password": "qP?34fQ%mC",
}


class TravelportHotelAdapter(HotelAdapter):
    def __init__(self, transport: TravelportTransport = None):
        if transport is None:
            self.transport = TravelportTransport()

    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelAdapterHotel]:
        hotel_search_service = self.transport.create_hotel_search_service()
        request = TravelportHotelSearchBuilder().build(search_request)
        response = hotel_search_service.service(**request)

        hotel_response = response["HotelSuperShopperResults"]
        hotels_with_rates = filter(lambda x: x["HotelRateDetail"], hotel_response)

        return list(map(self._parse_hotel, hotels_with_rates))

    def details(self, hotel_details: HotelDetailsSearchRequest) -> HotelDetails:
        hotel_details_service = self.transport.create_hotel_details_service()
        request = TravelportHotelDetailsBuilder.build(hotel_details)
        response = hotel_details_service.service(**request)

        return self._parse_details(response)

    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponseHotel:
        pass

    def booking_availability(self, search_request: HotelSpecificSearch):
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass

    def _parse_hotel(self, hotel):
        hotel_property = hotel["HotelProperty"]
        chain = hotel_property["HotelChain"]
        name = hotel_property["Name"]

        tax, total = self._parse_hotel_min_max_rate(hotel)
        address = self._parse_hotel_address(hotel_property)

        hotel_rate = HotelRate(total, tax)
        star_rating = self._parse_hotel_star_rating(hotel_property)

        return HotelAdapterHotel(name=name, chain_code=chain, address=address, rate=hotel_rate, star_rating=star_rating)

    @staticmethod
    def _parse_hotel_address(hotel_property):
        address_list = hotel_property["PropertyAddress"]["Address"]
        if len(address_list) >= 5:
            address, city, state, postal_code, country = address_list
            return Address(city, state, postal_code, country, address1=address)
        else:
            address, city, *_ = address_list

        return address

    @staticmethod
    def _parse_hotel_min_max_rate(hotel):
        rate = hotel["HotelRateDetail"][0]
        total = rate["Total"][3:]

        if rate["Tax"]:
            tax = rate["Tax"][3:]
        else:
            tax = 0.00

        return tax, total

    @staticmethod
    def _parse_hotel_star_rating(hotel) -> Optional[int]:
        return next(map(lambda x: x.Rating, hotel["HotelRating"]), None)

    def _parse_details(self, hotel_details):
        hotel = hotel_details["RequestedHotelDetails"]
        hotel_property = hotel["HotelProperty"]
        chain = hotel_property["HotelChain"]
        hotel_code = hotel_property["HotelCode"]
        name = hotel_property["Name"]

        details = hotel["HotelDetailItem"]
        checkin_time = next(x["Text"] for x in details if x["Name"] == "CheckInTime")[0]
        checkout_time = next(x["Text"] for x in details if x["Name"] == "CheckOutTime")[0]

        room_type_rates = list(map(self._parse_rate_detail, hotel["HotelRateDetail"]))

        geolocation = GeoLocation(0.0, 0.0)
        address = self._parse_hotel_address(hotel_property)

        return HotelDetails(
            name=name,
            address=address,
            chain_code=chain,
            hotel_code=hotel_code,
            checkin_time=checkin_time,
            checkout_time=checkout_time,
            hotel_rates=room_type_rates,
            geolocation=geolocation,
            phone_number=None,
            email=None,
            homepage_url=None,
            photos=[],
        )

    def _parse_rate_detail(self, rate_detail):
        rate_plan_type = rate_detail["RatePlanType"]
        rate_description = rate_detail["RoomRateDescription"]
        room_description = next(x["Text"] for x in rate_description if x["Name"] == "Room")[0]
        additional_description = next(x["Text"] for x in rate_description if x["Name"] == "Description")

        total_base_rate = self._parse_money(rate_detail["Base"])
        total_tax_rate = self._parse_money(rate_detail["Tax"])
        total_total_rate = self._parse_money(rate_detail["Total"])

        hotel_rates_by_date = []
        for hotel_rate_by_date in rate_detail["HotelRateByDate"]:
            effective_date = date.fromisoformat(hotel_rate_by_date["EffectiveDate"])
            expire_date = date.fromisoformat(hotel_rate_by_date["ExpireDate"])

            base_rate = self._parse_money(hotel_rate_by_date["Base"])
            tax_rate = self._parse_money(hotel_rate_by_date["Tax"])
            total_rate = self._parse_money(hotel_rate_by_date["Total"])

            # Travelport returns room type rates in a range
            # e.g., 2020-07-01 through 2020-07-03, and 2020-07-04 through 2020-07-07
            # we expand this into a separate rate for each day
            days_in_rate_schedule = (expire_date - effective_date).days
            for i in range(days_in_rate_schedule):
                rate_date = effective_date + timedelta(days=i)
                rate_detail = DailyRate(rate_date, base_rate, tax_rate, total_rate)
                hotel_rates_by_date.append(rate_detail)

        return RoomRate(
            room_description,
            additional_description,
            rate_plan_type,
            total_base_rate,
            total_tax_rate,
            total_total_rate,
            hotel_rates_by_date,
        )

    @staticmethod
    def _parse_money(money_str) -> Optional[Money]:
        if not money_str:
            return None

        currency = money_str[:3]
        amount = money_str[3:]

        return Money(float(amount), currency)