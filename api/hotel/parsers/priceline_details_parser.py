import requests

from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.models.models import supplier_priceline

amenities_dict = {
    "10": "Free Parking",
    "24": "Parking",
    "44": "Breakfast",
    "121": "Free Wi-Fi",
    "145": "Free Airport Shuttle",
    "146": "Kitchen",
    "748": "Pet Friendly",
    "1104": "Air Conditioned",
    "1316": "Casino Shuttle",
    "1955": "Water Park",
    "1019": "All Inclusive",
    "1375": "Spa",
    "1625": "Washer and Dryer",
    "1638": "Laundry Services",
    "2012": "Hot Tub",
    "2181": "Bar",
    "671": "Mini Bar",
    "1676": "Health Club or Gym",
    "1817": "Restaurant",
    "2106": "Dry Sauna",
}


class PricelineDetailsParser:
    def __init__(self, transport: PricelineTransport):
        self.transport = transport

    def load(self):
        resume_key = None
        while True:
            response = self.transport.hotels_download(resume_key=resume_key, limit=5)
            resume_key = response["getSharedBOF2.Downloads.Hotel.Hotels"]["results"]["resume_key"]
            hotel_data = response["getSharedBOF2.Downloads.Hotel.Hotels"]["results"]["hotels"]

            hotel_names = list(map(self.parse_hotel, hotel_data))
            print(hotel_names)

            break

    @staticmethod
    def parse_hotel(hotel_data):
        hotel_state = hotel_data["state"]
        amenities = []
        supplier = "Priceline"
        hotel_name = hotel_data["hotel_name"]
        hotel_address = hotel_data["hotel_address"]
        hotel_city = hotel_data["city"]
        hotel_country_code = hotel_data["country_code"]
        hotel_rating = hotel_data["star_rating"]
        hotel_description = hotel_data["property_description"]
        hotelid_ppn = hotel_data["hotelid_ppn"]
        cityid_ppn = hotel_data["cityid_ppn"]
        image_url_path = hotel_data["thumbnail"]

        return hotel_name