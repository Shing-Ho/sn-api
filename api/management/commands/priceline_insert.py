#!/usr/bin/env python
from django.core.management import BaseCommand
from api.models.models import supplier_priceline
import requests
import json

url = "https://api-sandbox.rezserver.com/api/shared/getBOF2.Downloads.Hotel.Hotels?refid=10046&api_key=990b98b0a0efaa7acf461ff6a60cf726&format=json"
# url = "https://api-sandbox.rezserver.com/api/hotel/getHotelDetails"
api_key = "990b98b0a0efaa7acf461ff6a60cf726"
ref_id = "10046"

amenities_dict = {'10':'Free Parking','24':'Parking','44':'Breakfast','121':'Free Wi-Fi','145':'Free Airport Shuttle',
    '146':'Kitchen',
    '748':'Pet Friendly',
    '1104':'Air Conditioned',
    '1316':'Casino Shuttle',
    '1955':'Water Park',
    '1019':'All Inclusive',
    '1375':'Spa',
    '1625':'Washer and Dryer',
    '1638':'Laundry Services',
    '2012':'Hot Tub',
    '2181':'Bar',
    '671':'Mini Bar',
    '1676':'Health Club or Gym',
    '1817':'Restaurant',
    '2106':'Dry Sauna'
                  }

class Command(BaseCommand):
    def handle(self, *args, **options):
        print('hello world')
        response = requests.get(url).json()
        hotel_data = response['getSharedBOF2.Downloads.Hotel.Hotels']['results']['hotels']
        # with open('hotel.json') as json_file:
        #     hotel_data = json.load(json_file)['getSharedBOF2.Downloads.Hotel.Hotels']['results']['hotels']

        # print(response['getSharedBOF2.Downloads.Hotel.Hotels']['results']['hotels']['hotel_4987'])
        # print(response['getSharedBOF2.Downloads.Hotel.Hotels']['results']['hotels'].keys())

        # count = 0
        for hotel in hotel_data.keys():
            print(hotel)
#   used for testing
#    while count == 0:
#        print(hotel_data[hotel].keys())
#        count +=1

            if hotel_data[hotel]['state'] == None:
                hotel_state = "no state"
            else:
                hotel_state = hotel_data[hotel]['state']
            amenities = []
            supplier            = 'Priceline'
            hotel_name          = hotel_data[hotel]['hotel_name']
            hotel_address       = hotel_data[hotel]['hotel_address']
            hotel_city          = hotel_data[hotel]['city']
            hotel_country_code  = hotel_data[hotel]['country_code']
            hotel_rating        = hotel_data[hotel]['star_rating']
            hotel_description   = hotel_data[hotel]['property_description']
            image_url_path      = hotel_data[hotel]['thumbnail']

            # romp through each item and append to our empty list
            if hotel_data[hotel]["amenity_codes"] != None:
                for item in list(hotel_data[hotel]['amenity_codes'].split("^")):
                    if item in amenities_dict.keys():
                        amenities.append(amenities_dict[item])
            # print(len(hotel_data.keys()))
            # print(amenities)


            # insert into sn db
                print('inserting')
                print(image_url_path)
                print(hotel_rating)
                try:
                    supplier_priceline.objects.update_or_create(
                    supplier = supplier, hotel_name = hotel_name, hotel_address = hotel_address,
                    hotel_city = hotel_city, hotel_state = hotel_state, hotel_country_code = hotel_country_code,
                    hotel_rating = hotel_rating, hotel_description = hotel_description,
                    hotel_amenities = amenities, image_url_path = image_url_path
                )
                except:
                    print("didtn insert for {}".format(hotel))
                print(supplier_priceline.objects.all().count())