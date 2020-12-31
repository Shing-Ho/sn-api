import requests

from api.charging.constants import CONFIG


class ChargingService:
    def __init__(self, env="development"):
        self.env = env
        self.config = CONFIG[env]
        self.api_key = self.config["api_key"]
    
    def generate_header(self):
        return {
            "X-API-Key": self.api_key
        }

    def get_poi(self, request):
        header = self.generate_header()

        country_code = request.GET.get("country_code")
        max_results = request.GET.get("max_results")
        client = request.GET.get("client")
        country_id = request.GET.get("country_id")
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        print(request.GET)

        url = self.config['end_point'] + "poi/?countrycode=" + country_code
        if max_results:
            url += "&maxresults=" + max_results
        if client:
            url += "&client=" + client
        if country_id:
            url += "&countryid=" + country_id
        if latitude:
            url += "&latitude=" + latitude
        if longitude:
            url += "&longitude=" + longitude

        response = requests.get(url, headers=header)
        return response
