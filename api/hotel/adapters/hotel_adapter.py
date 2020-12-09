import abc
from typing import List

from api.hotel.adapters import adapter_common
from api.hotel.models.booking_model import HotelBookingRequest, Reservation
from api.hotel.models.hotel_common_models import RoomRate, HotelReviews
from api.hotel import hotel_mappings
from api.hotel.models.hotel_api_model import (
    HotelSpecificSearch,
    AdapterHotel,
    HotelDetails,
)
from api.hotel.models.adapter_models import (
    AdapterHotelSearch,
    AdapterLocationSearch,
    AdapterCancelRequest,
    AdapterCancelResponse,
    AdapterHotelBatchSearch,
)
from api.locations import location_service
from api.view.exceptions import AvailabilityException, AvailabilityErrorCode


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search_by_location(self, search: AdapterLocationSearch) -> List[AdapterHotel]:
        """Search a provider for a particular location"""

    @abc.abstractmethod
    def search_by_id(self, search_request: AdapterHotelSearch) -> AdapterHotel:
        """Search a hotel provider for a specific hotel"""

    @abc.abstractmethod
    def search_by_id_batch(self, search_request: AdapterHotelBatchSearch) -> List[AdapterHotel]:
        """Search for several hotels by hotel ID."""

    @abc.abstractmethod
    def details(self, *args) -> HotelDetails:
        """Return Hotel Details using a hotel provider"""

    @abc.abstractmethod
    def reviews(self, *args) -> HotelReviews:
        """Returns an object containing an average user review, and a list of user reviews for a hotel"""

    @abc.abstractmethod
    def booking(self, book_request: HotelBookingRequest) -> Reservation:
        """Given a HotelBookingRequest, confirm a reservation with a hotel provider"""

    @abc.abstractmethod
    def recheck(self, room_rate: RoomRate) -> RoomRate:
        """Given a list of RoomRates, recheck prices, and return verified RoomRates"""

    @abc.abstractmethod
    def cancel(self, cancel_request: AdapterCancelRequest) -> AdapterCancelResponse:
        """Given an adapter record locator, cancel a booking."""

    @classmethod
    @abc.abstractmethod
    def factory(cls, test_mode=True):
        pass

    @classmethod
    @abc.abstractmethod
    def get_provider_name(cls):
        pass

    def get_provider_location(self, search_request: AdapterLocationSearch):
        return adapter_common.get_provider_location(self.get_provider_name(), search_request.location_id)

    def get_provider_hotel_mapping(self, search_request: HotelSpecificSearch):
        return hotel_mappings.find_provider_hotel_id(search_request.hotel_id, self.get_provider_name())
