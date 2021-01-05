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
        url = self.config['end_point'] + "poi/?"
        for param in request.GET:
            url += param + "=" + request.GET.get(param) + "&" 

        response = requests.get(url, headers=self.generate_header())
        return response

    def get_reference(self, request):
        url = self.config['end_point'] + "referencedata/?"
        for param in request.GET:
            url += param + "=" + request.GET.get(param) + "&" 

        response = requests.get(url, headers=self.generate_header())
        return response

    def post_comment(self, request):
        url = self.config['end_point'] + "?action=comment_submission&format=json"

        response = requests.post(url, data=request.data, headers=self.generate_header())
        return response
