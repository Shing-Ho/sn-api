from api.hotel.adapters.adapter_info import AdapterInfo


class TripservicesInfo(AdapterInfo):
    name = "tripservices"

    def get_name(self):
        return self.name
