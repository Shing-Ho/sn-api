from api.hotel.adapters.adapter_info import AdapterInfo


class PricelineInfo(AdapterInfo):
    name = "priceline"

    def get_name(self):
        return self.name
