from django.core.management import BaseCommand
from api.models.models import hotelmappingcodes, sn_hotel_map
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
            "model": hotelmappingcodes, "name": "HotelBeds"}}

        for table in main_dict.keys():
            for hotel in main_dict[table]["model"].objects.all():
                name = table
                print({"provider": main_dict[table]["name"]})
                print(hotel.hotel_codes)

                sn_id = random.choice(random_ids)
                random_ids.remove(sn_id)
                sn_hotel_map.objects.update_or_create(
                    simplenight_id=sn_id,
                    provider=main_dict[table]["name"],
                    provider_id=hotel.hotel_codes
                )
