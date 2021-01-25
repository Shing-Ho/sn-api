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
from api.activities.activity_models import (
    SimplenightActivityDetailResponse,
    ActivityAvailabilityTime,
    ActivityCancellation,
    ActivityItem,
    ActivityVariants,
)
from api.activities.adapters.suppliers_api import suppliers_api_util
from api.activities.adapters.suppliers_api.suppliers_api_transport import SuppliersApiTransport
from api.common.common_models import BusinessContact, BusinessLocation
from api.hotel.models.booking_model import ActivityBookingRequest, Customer, Locator
from api.hotel.models.hotel_api_model import Image, ImageType
from api.hotel.models.hotel_common_models import Money


class SuppliersApiActivityAdapter(ActivityAdapter, abc.ABC):
    def __init__(self, transport: SuppliersApiTransport):
        self.transport = transport

    async def search_by_location(self, search: AdapterActivityLocationSearch) -> List[AdapterActivity]:
        request_params = self._get_search_params(search)
        logger.info(f"Searching {self.get_provider_name()} with params: {request_params}")
        response = self.transport.search(**request_params)

        return list(map(lambda x: self._create_activity(x, activity_date=search.begin_date), response["data"]))

    async def search_by_id(self, search: AdapterActivitySpecificSearch) -> AdapterActivity:
        raise NotImplementedError("Search by ID Not Implemented")

    async def book(self, booking_request: ActivityBookingRequest, customer: Customer) -> AdapterActivityBookingResponse:
        params = {
            "code": booking_request.code,
            "date": str(booking_request.activity_date),
            "time": str(booking_request.activity_time),
            "currency": booking_request.currency,
            "booking": {
                "customer": {
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "email": customer.email,
                    "phone": customer.phone_number,
                    "locale": booking_request.language_code,
                }
            },
            "items": [
                {
                    "code": booking_request.items[0].code,
                    "quantity": 1,
                    "supplier_proceeds": str(booking_request.items[0].price),
                    "date": str(booking_request.activity_date),
                }
            ],
        }

        response = self.transport.book(**params)
        return AdapterActivityBookingResponse(
            success=response["success"], record_locator=Locator(id=response["order_id"])
        )

    async def details(self, product_id: str, date_from: date, date_to: date) -> SimplenightActivityDetailResponse:
        response = self.transport.details(product_id, date_from, date_to)
        details = self._create_details(response)

        return details

    async def variants(self, product_id: str, activity_date: date) -> List[ActivityVariants]:
        response = self.transport.variants(product_id, activity_date)
        return list(map(self._parse_variants, response))

    async def cancel(self, order_id: str) -> bool:
        pass

    @staticmethod
    def _parse_variants(variant):
        return ActivityVariants(
            code=variant["code"],
            name=list(variant["name"].values())[0],
            description=list(variant["description"].values())[0],
            capacity=variant["capacity"],
            status=variant["status"],
            price=Decimal(variant["price"]),
            currency=variant["currency"],
        )

    @staticmethod
    def _parse_image(image: Dict, display_order: int) -> Image:
        return Image(url=image["url"], type=ImageType.UNKNOWN, display_order=display_order)

    @staticmethod
    def _parse_location(location):
        return BusinessLocation(
            latitude=location["latitude"], longitude=location["longitude"], address=location["address"]
        )

    @staticmethod
    def _parse_availability(availability):
        if availability["type"] == "SINGLE":
            schedule = [date.fromisoformat(availability["date"])]
        elif availability["type"] in ("RANGE", "ALWAYS"):
            schedule = suppliers_api_util.expand_schedule(availability)
        else:
            schedule = []

        return ActivityAvailabilityTime(
            type=availability["type"],
            label=availability["label"],
            activity_dates=schedule,
            activity_times=availability["times"],
            capacity=availability["capacity"],
            uuid=availability["uuid"],
        )

    @staticmethod
    def _parse_cancellation_policy(policy):
        return ActivityCancellation(type=policy["type"], label=policy["label"])

    @staticmethod
    def _parse_activity_items(item):
        return ActivityItem(
            category=item["categories"],
            code=item["code"],
            status=item["status"],
            price=Decimal(item["price"]),
            price_type=item["price_type"],
        )

    def _create_details(self, detail):
        availabilities = map(lambda x: self._parse_availability(x), detail["availabilities"])
        availabilities = filter(None, availabilities)

        return SimplenightActivityDetailResponse(
            code=detail["code"],
            type=detail["type"],
            categories=detail["categories"],
            timezone=detail["timezone"],
            images=list(self._parse_image(image, idx) for idx, image in enumerate(detail["images"])),
            contact=BusinessContact(
                name=detail["contact"]["name"],
                email=detail["contact"]["email"],
                website=detail["contact"]["website"],
                address=detail["contact"]["address"],
                phones=detail["contact"]["phones"],
            ),
            locations=list(map(self._parse_location, detail["locations"])),
            availabilities=list(availabilities),
            policies=detail["policies"],
            cancellations=list(map(self._parse_cancellation_policy, detail["cancellations"])),
            items=list(map(self._parse_activity_items, detail["items"])),
        )

    def _create_activity(self, activity, activity_date: date):
        return AdapterActivity(
            name=activity["name"],
            provider=self.get_provider_name(),
            code=activity["code"],
            description=activity["description"],
            activity_date=activity_date,
            total_price=Money(amount=activity["price"], currency=activity["currency"]),
            total_base=Money(amount=Decimal(0), currency=activity["currency"]),
            total_taxes=Money(amount=Decimal(0), currency=activity["currency"]),
            images=list(self._parse_image(image, idx) for idx, image in enumerate(activity["images"])),
        )

    @staticmethod
    def _get_search_params(search: AdapterActivityLocationSearch) -> Dict[Any, Any]:
        return {
            "date_from": str(search.begin_date),
            "date_to": str(search.end_date),
            "location": {"longitude": str(search.location.longitude), "latitude": str(search.location.latitude)},
        }
