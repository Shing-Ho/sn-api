import abc
from datetime import date
from decimal import Decimal
from typing import List, Any, Dict

from api import logger
from api.activities.activity_adapter import ActivityAdapter
from api.activities.activity_internal_models import (
    AdapterActivity,
    AdapterActivitySpecificSearch,
    AdapterActivityLocationSearch,
    AdapterActivityBookingResponse,
)
from api.activities.activity_models import SimplenightActivityDetailResponse
from api.activities.adapters.suppliers_api.suppliers_api_transport import SuppliersApiTransport
from api.common.common_models import from_json
from api.hotel.models.booking_model import ActivityBookingRequest, Customer
from api.hotel.models.hotel_api_model import Image, ImageType
from api.hotel.models.hotel_common_models import Money
from api.view.exceptions import AvailabilityException, AvailabilityErrorCode


class SuppliersApiActivityAdapter(ActivityAdapter, abc.ABC):
    def __init__(self, transport: SuppliersApiTransport):
        self.transport = transport

    async def search_by_location(self, search: AdapterActivityLocationSearch) -> List[AdapterActivity]:
        request_params = self._get_search_params(search)
        logger.info(f"Searching {self.get_provider_name()} with params: {request_params}")
        response = self.transport.search(**request_params)
        if "code" not in response or response["code"] != 200:
            logger.error(f"Error Searching Suppliers API: {response}")
            raise AvailabilityException("Error searching suppliers_api", AvailabilityErrorCode.PROVIDER_ERROR)

        return list(map(lambda x: self._create_activity(x, activity_date=search.begin_date), response["data"]))

    async def search_by_id(self, search: AdapterActivitySpecificSearch) -> AdapterActivity:
        raise NotImplementedError("Search by ID Not Implemented")

    async def book(self, booking_request: ActivityBookingRequest, customer: Customer) -> AdapterActivityBookingResponse:
        params = {
            "uuid": booking_request.code,
            "lang": booking_request.language_code,
            "date": str(booking_request.activity_date),
            "time": str(booking_request.activity_time),
            "currency": booking_request.currency,
            "customer": {
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "phone": customer.phone_number,
            },
            "items": [
                {"code": booking_request.items[0].code, "quantity": 1, "price": str(booking_request.items[0].price)}
            ],
        }

        response = self.transport.book(**params)
        print(response)

    async def details(self, product_id: str, date_from: date, date_to: date) -> SimplenightActivityDetailResponse:
        params = {"uuid": product_id}

        response = self.transport.details(date_from, date_to, **params)
        details = from_json(response, SimplenightActivityDetailResponse)

        return details

    async def cancel(self, order_id: str) -> bool:
        pass

    def _create_activity(self, activity, activity_date: date):
        def _parse_image(image: Dict) -> Image:
            return Image(url=image["url"], type=ImageType.UNKNOWN)

        return AdapterActivity(
            name=activity["name"],
            provider=self.get_provider_name(),
            code=activity["code"],
            description="",
            activity_date=activity_date,
            total_price=Money(amount=activity["price"], currency=activity["currency"]),
            total_base=Money(amount=Decimal(0), currency=activity["currency"]),
            total_taxes=Money(amount=Decimal(0), currency=activity["currency"]),
            images=list(map(_parse_image, activity["images"])),
        )

    @staticmethod
    def _get_search_params(search: AdapterActivityLocationSearch) -> Dict[Any, Any]:
        return {
            "date_from": str(search.begin_date),
            "date_to": str(search.end_date),
            "location": {"longitude": str(search.location.longitude), "latitude": str(search.location.latitude)},
        }
