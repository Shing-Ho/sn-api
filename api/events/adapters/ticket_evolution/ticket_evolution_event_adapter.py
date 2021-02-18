from typing import Dict, List

from api import logger
from api.events.adapters.ticket_evolution.ticket_evolution_event_transport import TicketEvolutionEventTransport
from api.events.event_adapter import EventAdapter
from api.events.events_models import EventAdapterLocationSearch, AdapterEvent, EventLocation, EventItem
from api.hotel.models.hotel_api_model import Image
from api.hotel.models.hotel_common_models import Money


class TicketEvolutionEventAdapter(EventAdapter):
    def __init__(self, transport: TicketEvolutionEventTransport):
        self.transport = transport

    async def search_by_location(self, search: EventAdapterLocationSearch):
        endpoint = TicketEvolutionEventTransport.Endpoint.SEARCH

        try:
            search_params = self._get_search_params(search)
            logger.info(f"Params: {search_params}")
            results = self.transport.post(endpoint, **search_params)
            return list(map(self._create_event, results["result"]))
        except Exception:
            logger.exception(f"Caught exception while searching {self.get_provider_name()}")

    def _create_event(self, event: Dict):
        details = event["details"]

        return AdapterEvent(
            provider=self.get_provider_name(),
            code=event["code"],
            name=details["name"]["en"],
            description=details["description"]["en"],
            seating_chart=event["features"]["seating_chart"],
            location=self._create_location(event),
            categories=event["categories"],
            images=self._create_images(event["images"]),
            items=self._create_items(event["items"], event["currency"]),
        )

    @staticmethod
    def _create_items(items: Dict, currency: str):
        def create_item(item: Dict):
            return EventItem(
                code=item["code"], price=Money(amount=item["price"], currency=currency), name=item["name"]["en"],
            )

        return list(create_item(item) for item in items)

    @staticmethod
    def _create_images(images: List[Dict]):
        return list(Image(url=image["url"], display_order=idx) for idx, image in enumerate(images))

    @staticmethod
    def _create_location(event: Dict):
        try:
            return EventLocation(
                name=event["contact"]["name"],
                address=event["contact"]["address"],
                latitude=event["locations"][0]["latitude"],
                longitude=event["locations"][0]["longitude"],
            )
        except KeyError:
            return None

    @staticmethod
    def _get_search_params(search: EventAdapterLocationSearch):
        return {
            "date_from": str(search.begin_date),
            "date_to": str(search.end_date),
            "location": {"latitude": float(search.location.latitude), "longitude": float(search.location.longitude),},
        }

    @classmethod
    def factory(cls, test_mode=True):
        return TicketEvolutionEventAdapter(TicketEvolutionEventTransport(test_mode=test_mode))

    @classmethod
    def get_provider_name(cls):
        return "ticket_evolution"
