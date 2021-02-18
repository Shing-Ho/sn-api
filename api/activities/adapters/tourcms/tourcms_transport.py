from api.common.simplenight_core_legacy_transport import SimplenightCoreLegacyTransport


class TourCmsTransport(SimplenightCoreLegacyTransport):
    @staticmethod
    def get_supplier_name():
        return "grayline-lasvegas"
