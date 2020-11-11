import abc
from typing import List

from api.hotel.models.booking_model import HotelBookingRequest, Reservation
from api.hotel.models.hotel_common_models import RoomRate
from api.hotel import hotel_mappings
from api.hotel.models.hotel_api_model import (
    HotelSpecificSearch,
    AdapterHotel,
    HotelDetails,
)
from api.hotel.models.adapter_models import AdapterHotelSearch, AdapterLocationSearch, AdapterCancelRequest, \
    AdapterCancelResponse, AdapterHotelBatchSearch
from api.locations import location_service
from api.view.exceptions import AvailabilityException, AvailabilityErrorCode


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search_by_location(self, search: AdapterLocationSearch) -> List[AdapterHotel]:
        """Search a provider for a particular location"""
        pass

    @abc.abstractmethod
    def search_by_id(self, search_request: AdapterHotelSearch) -> AdapterHotel:
        """Search a hotel provider for a specific hotel"""
        pass

    @abc.abstractmethod
    def search_by_id_batch(self, search_request: AdapterHotelBatchSearch) -> List[AdapterHotel]:
        """Search for several hotels by hotel ID."""
        pass

    @abc.abstractmethod
    def details(self, *args) -> HotelDetails:
        """Return Hotel Details using a hotel provider"""
        pass

    @abc.abstractmethod
    def booking(self, book_request: HotelBookingRequest) -> Reservation:
        """Given a HotelBookingRequest, confirm a reservation with a hotel provider"""
        pass

    @abc.abstractmethod
    def recheck(self, room_rate: RoomRate) -> RoomRate:
        """Given a list of RoomRates, recheck prices, and return verified RoomRates"""
        pass

    @abc.abstractmethod
    def cancel(self, cancel_request: AdapterCancelRequest) -> AdapterCancelResponse:
        """Given an adapter record locator, cancel a booking."""
        pass

    @classmethod
    @abc.abstractmethod
    def factory(cls, test_mode=True):
        pass

    @classmethod
    @abc.abstractmethod
    def get_provider_name(cls):
        pass

    def get_provider_location(self, search_request: AdapterLocationSearch):
        provider_location = location_service.find_provider_location(
            self.get_provider_name(), search_request.location_id
        )

        if provider_location is None:
            raise AvailabilityException(
                detail="Could not find provider location mapping", error_type=AvailabilityErrorCode.LOCATION_NOT_FOUND
            )

        return provider_location

    def get_provider_hotel_mapping(self, search_request: HotelSpecificSearch):
        return hotel_mappings.find_provider_hotel_id(search_request.hotel_id, self.get_provider_name())
