from api import logger
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.models.models import ProviderHotel

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
        self.priceline = PricelineAdapter(transport=transport)
        self.provider = self.priceline.adapter_info.get_or_create_provider_id()

    def load(self, limit=None):
        total_loaded = 0
        resume_key = None

        ProviderHotel.objects.filter(provider=self.provider).delete()

        while True:
            response = self.transport.hotels_download(resume_key=resume_key, limit=1000)
            resume_key = response["getSharedBOF2.Downloads.Hotel.Hotels"]["results"]["resume_key"]
            hotel_data = response["getSharedBOF2.Downloads.Hotel.Hotels"]["results"]["hotels"]

            models = list(map(self.parse_hotel, hotel_data))
            ProviderHotel.objects.bulk_create(models)
            total_loaded += len(models)

            logger.info(f"Loaded {total_loaded} hotels")
            if resume_key is None:
                logger.info(f"Complete loading hotels")
                return

            if limit and total_loaded >= limit:
                logger.info(f"Reached loading limit of {limit}")
                return

    def parse_hotel(self, hotel_data):
        amenities = []
        amenities_response = hotel_data["amenity_codes"]
        if amenities_response:
            amenities = amenities_response.split("^")

        return ProviderHotel(
            provider=self.provider,
            language_code="en",
            provider_code=hotel_data["hotelid_ppn"],
            hotel_name=hotel_data["hotel_name"],
            city_name=hotel_data["city"],
            state=hotel_data["state"],
            country_code=hotel_data["country_code"],
            address_line_1=hotel_data["hotel_address"],
            postal_code=hotel_data["postal_code"],
            latitude=hotel_data["latitude"],
            longitude=hotel_data["longitude"],
            thumbnail_url=hotel_data["thumbnail"],
            star_rating=hotel_data["star_rating"],
            property_description=hotel_data["property_description"],
            amenities=amenities,
        )
