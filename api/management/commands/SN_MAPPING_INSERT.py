from django.db.models import Q
import re
from fuzzywuzzy import fuzz
import pandas as pd
from api.models.models import supplier_hotels, sn_hotel_map
from django.core.management import BaseCommand
import random

'''
Must import all models such as hotelbeds as we must check if these is already a key for a specific hotel.
Search first, to see if we have an existing SN hotel id. If we do apply that to corresponding hotel and provider name
Otherwise create a SN id for hotel. In the case of starting hotelbeds we would be intitally doing all creates

'''
# matching on city might not be best...


def find_other_properties(address, city, country, provider):
    ''' first step isolate by city and country '''
    try:
        street_nums = str(re.search(r'\d+', address).group())
    except:
        street_nums = "nothing found here"
    hotels = supplier_hotels.objects.filter(
        city=city, country_name=country, address__contains=street_nums)
    ratios = []
    count = -1
    index = []
    matches = []
    for item in hotels:
        count += 1
        if fuzz.ratio(item.address, address) > 75:
            ratios.append(count)
    for index in ratios:
        matches.append(hotels[index])

    return matches


class Command(BaseCommand):
    def handle(self, *args, **options):
        sn_hotel_map.objects.all().delete()
        random_ids = []

        for i in range(10000, 999999):
            random_ids.append(i)
        main_dict = {"hotelbeds": {
            "model": supplier_hotels, "name": "HotelBeds"}}

        for table in main_dict.keys():
            for hotel in main_dict[table]["model"].objects.all():
                temp_sn_id = 0
                potential_matches = (find_other_properties(
                    hotel.address, hotel.city, hotel.country_name, hotel.provider_name))
                for x in potential_matches:
                    print(x.hotel_codes)
                    match_query = sn_hotel_map.objects.filter(
                        provider_id=x.hotel_codes)
                    if len(match_query) > 0:
                        temp_sn_id = match_query[0].simplenight_id

                        print(temp_sn_id)
                    else:
                        temp_sn_id = 0
                if sn_hotel_map.objects.filter(provider_id=hotel.hotel_codes).count() > 0:
                    # dont do anything we already have this in the database
                    print("skipping")

                else:
                    print({"provider": hotel.provider_name})
                    print(hotel.hotel_codes)

                    # grab an a radom number from our list
                    # and assign as our sn id
                    if temp_sn_id == 0 or temp_sn_id == None:
                        sn_id = random.choice(random_ids)
                    else:
                        sn_id = temp_sn_id
                    random_ids.remove(sn_id)
                    # then simply just create the objects
                    # if that simple night id is already in there (from a previous run) then do not use it again
                    while sn_hotel_map.objects.filter(simplenight_id=sn_id).count() > 0:
                        sn_id = random.choice(random_ids)
                    # then remove so we arnt using the same id twice
                        random_ids.remove(sn_id)
                    # then simply just create the objects

                    sn_hotel_map.objects.update_or_create(
                        simplenight_id=sn_id,
                        provider=hotel.provider_name,
                        provider_id=hotel.hotel_codes
                    )
                    print("its been added")
