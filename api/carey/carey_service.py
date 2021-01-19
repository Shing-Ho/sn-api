from api.carey.adapters.carey_adapter import CareyAdapter


class CareyService:
    def __init__(self, carey: CareyAdapter = None):
        if carey is None:
            self.carey = CareyAdapter()

    def get_wsdl_url(self):
        return "https://sandbox.carey.com/CSIOTAProxy_v2/CareyReservationService?wsdl"

    def get_quote_inquiry(self, request):
        response = self.carey.get_rate_inquiry(request)
        return response

    def get_book_reservation(self, request):
        response = self.carey.get_book_reservation(request)
        return response

    def get_modify_reservation(self, request):
        response = self.carey.get_modify_reservation(request)
        return response

    def get_find_reservation(self, request):
        response = self.carey.get_find_reservation(request)
        return response

    def get_cancel_reservation(self, request):
        response = self.carey.get_cancel_reservation(request)
        return response
