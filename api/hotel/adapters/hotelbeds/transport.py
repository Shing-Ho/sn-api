import hashlib
import time

from api.hotel.adapters.transport import Transport


class HotelBedsTransport(Transport):
    def get_headers(self, **kwargs):
        headers = self._get_default_headers()
        headers["Content-Type"] = "application/json"
        headers["Api-Key"] = self._get_apikey()
        headers["X-Signature"] = self._get_xsignature()
        headers.update(kwargs)

        return headers

    @staticmethod
    def _get_apikey():
        return "ba99fa9f7b504eae563b35b294ef2dcc"

    @staticmethod
    def _get_secret():
        return "2e4a7d611f"

    @classmethod
    def _get_xsignature(cls):
        current_time_in_seconds = int(time.time())
        signature_str = f"{cls._get_apikey()}{cls._get_secret()}{current_time_in_seconds}"
        return hashlib.sha256(signature_str.encode()).hexdigest()

    @classmethod
    def get_hotels_url(cls):
        return f"{cls._get_base_booking_url()}/hotels"

    @classmethod
    def get_booking_url(cls):
        return f"{cls._get_base_booking_url()}/bookings"

    @classmethod
    def get_checkrates_url(cls):
        return f"{cls._get_base_booking_url()}/checkrates"

    @classmethod
    def get_hotel_content_url(cls):
        return f"{cls._get_base_content_url()}/hotels"

    @classmethod
    def get_facilities_types_url(cls):
        return f"{cls._get_base_content_url()}/types/facilities"

    @classmethod
    def _get_base_booking_url(cls):
        return f"{cls._get_base_url()}/hotel-api/1.0"

    @classmethod
    def _get_base_content_url(cls):
        return f"{cls._get_base_url()}/hotel-content-api/1.0"

    @classmethod
    def _get_base_url(cls):
        return "https://api.test.hotelbeds.com"
