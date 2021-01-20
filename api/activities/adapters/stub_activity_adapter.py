import random
from datetime import datetime, date
from decimal import Decimal
from typing import List

from api.activities.activity_adapter import ActivityAdapter
from api.activities.activity_internal_models import (
    AdapterActivitySpecificSearch,
    AdapterActivityLocationSearch,
    AdapterActivitySearch,
    AdapterActivityBookingResponse,
)
from api.activities.activity_models import SimplenightActivity
from api.hotel.models.booking_model import ActivityBookingRequest
from api.hotel.models.hotel_common_models import Money


class StubActivityAdapter(ActivityAdapter):
    async def search_by_location(self, search: AdapterActivityLocationSearch) -> List[SimplenightActivity]:
        return list(self._create_activity_product(search) for _ in range(random.randint(2, 25)))

    async def search_by_id(self, search: AdapterActivitySpecificSearch) -> SimplenightActivity:
        return self._create_activity_product(search)

    async def details(self, product_id: str, date_from: date, date_to: date) -> AdapterActivityBookingResponse:
        raise NotImplementedError("Details Not Implemented")

    async def cancel(self, order_id: str) -> bool:
        raise NotImplementedError("Cancel not implemented")

    async def booking(self, booking_request: ActivityBookingRequest) -> AdapterActivityBookingResponse:
        raise NotImplementedError("Booking not implemented in Stub adapter")

    def _create_activity_product(self, search: AdapterActivitySearch):
        tour_name, activity, tour_type, activity_name = self._create_activity_name()
        description = self._create_activity_description(tour_name, activity, tour_type)
        total_base = Money(amount=Decimal(random.random() * 400), currency="USD")
        total_taxes = Money(amount=Decimal(random.random() * 25), currency="USD")
        total_price = Money(amount=total_base.amount + total_taxes.amount, currency="USD")

        return SimplenightActivity(
            name=activity_name,
            description=description,
            activity_date=datetime.now(),
            total_price=total_price,
            total_base=total_base,
            total_taxes=total_taxes,
            images=[],
        )

    @staticmethod
    def _create_activity_name():
        name = random.choice(["Acme", "Wonder", "Bob's", "Joe's"])
        activity = random.choice(["Dolphin", "Shark", "Cliff Climbing", "Biking", "Trek"])
        tour_type = random.choice(["Excusion", "Tour", "Experiences", "Escape"])

        return name, activity, tour_type, f"{name} {activity} {tour_type}"

    @staticmethod
    def _create_activity_description(name, activity, tour_type):
        return (
            f"Escape the city and go on an exciting "
            f"{activity.lower()} {tour_type.lower()} with {name} {activity} {tour_type}"
        )

    @classmethod
    def factory(cls, test_mode=True):
        return StubActivityAdapter()

    @classmethod
    def get_provider_name(cls):
        return "stub_activity"
