from api.activities.adapters.legacy_base_adapter.simplenight_core_legacy_adapter import SimplenightCoreLegacyBaseAdapter
from api.activities.adapters.tourcms.tourcms_transport import TourCmsTransport


class TourCmsTransportSimplenightCore(SimplenightCoreLegacyBaseAdapter):
    @classmethod
    def factory(cls, test_mode=True):
        return TourCmsTransportSimplenightCore(TourCmsTransport(test_mode=test_mode))

    @classmethod
    def get_provider_name(cls):
        return "tourcms"
