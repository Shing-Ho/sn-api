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
)
from api.activities.adapters.suppliers_api.suppliers_api_transport import SuppliersApiTransport
from api.hotel.models.hotel_api_model import Image, ImageType
from api.hotel.models.hotel_common_models import Money
from api.view.exceptions import AvailabilityException, AvailabilityErrorCode


class SuppliersApiActivityAdapter(ActivityAdapter, abc.ABC):
    def __init__(self, transport: SuppliersApiTransport):
        self.transport = transport

    async def search_by_location(self, search: AdapterActivityLocationSearch) -> List[AdapterActivity]:
        request_params = self._get_search_params(search)
        response = self.transport.search(**request_params)
        if "code" not in response or response["code"] != 200:
            logger.error(f"Error Searching Suppliers API: {response}")
            raise AvailabilityException("Error searching suppliers_api", AvailabilityErrorCode.PROVIDER_ERROR)

        return list(map(lambda x: self._create_activity(x, activity_date=search.begin_date), response["data"]))

    async def search_by_id(self, search: AdapterActivitySpecificSearch) -> AdapterActivity:
        raise NotImplementedError("Search by ID Not Implemented")

    @staticmethod
    def _create_activity(activity, activity_date: date):
        def _parse_image(image: Dict) -> Image:
            return Image(url=image["url"], type=ImageType.UNKNOWN)

        return AdapterActivity(
            name=activity["name"],
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

    @classmethod
    def get_provider_name(cls):
        return "suppliers_api"
