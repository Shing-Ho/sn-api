from enum import Enum

from api.common.simplenight_core_legacy_transport import SimplenightCoreLegacyTransport


class TicketEvolutionEventTransport(SimplenightCoreLegacyTransport):
    class Endpoint(Enum):
        SEARCH = "search"

    @staticmethod
    def get_supplier_name():
        return "ticketevolution-live"
