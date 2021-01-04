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

        url = self.config['end_point'] + "poi/?"
        for param in request.GET:
            url += param + "=" + request.GET.get(param) + "&" 

        response = requests.get(url, headers=header)
        return response
