from django.core.management import BaseCommand
from api.models.models import supplier_hotels, sn_hotel_map
import pandas as pd

'''
Must import all models such as hotelbeds as we must check if these is already a key for a specific hotel. 
Search first, to see if we have an existing SN hotel id. If we do apply that to corresponding hotel and provider name
Otherwise create a SN id for hotel. In the case of starting hotelbeds we would be intitally doing all creates 

'''

import random


class Command(BaseCommand):
    def handle(self, *args, **options):
        random_ids = []

        for i in range(10000, 999999):
            random_ids.append(i)
        main_dict = {"hotelbeds": {
            "model": supplier_hotels, "name": "HotelBeds"}}

        for table in main_dict.keys():
            for hotel in main_dict[table]["model"].objects.all():
                if sn_hotel_map.objects.filter(provider_id=hotel.hotel_codes).count() > 0:
                    # dont do anything we already have this in the database
                    print("skipping")

                else:
                    name = table
                    # for address in main_dict.keys():
                    #     if main_dict[]
                    print({"provider": main_dict[table]["name"]})
                    print(hotel.hotel_codes)
                    # grab an a radom number from our list
                    # and assign as our sn id
                    sn_id = random.choice(random_ids)
                    # then remove so we arnt using the same id twice
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
                        provider=main_dict[table]["name"],
                        provider_id=hotel.hotel_codes
                    )
                    print("its been added")
