from django.core.management import BaseCommand
from api.models.models import supplier_hotels, sn_city_map
import pandas as pd


import random


def get_sn_id(data):
    search =


class Command(BaseCommand):
    def handle(self, *args, **options):
        random_ids = []

        for i in range(10000, 99999):
            random_ids.append(i)
        main_dict = {"hotelbeds": {
            "model": supplier_hotels, "name": "HotelBeds"}}

        for table in main_dict.keys():
            for hotel in main_dict[table]["model"].objects.all():
                if sn_city_map.objects.filter(provider_city_name=str("{},{}").format(hotel.city, hotel.postal_code)).count() > 0:
                    # dont do anything we already have this in the database
                    print("skipping")

                else:
                    name = table

                    print({"provider": main_dict[table]["name"]})
                    print(hotel.city)

                    sn_id = random.choice(random_ids)
                    # then remove so we arnt using the same id twice
                    random_ids.remove(sn_id)
                    # then simply just create the objects
                    # if that simple night id is already in there (from a previous run) then do not use it again
                    while sn_city_map.objects.filter(simplenight_city_id=sn_id).count() > 0:
                        sn_id = random.choice(random_ids)
                    # then remove so we arnt using the same id twice
                        random_ids.remove(sn_id)
                    # then simply just create the objects

                    sn_city_map.objects.update_or_create(
                        simplenight_city_id=sn_id,
                        provider=main_dict[table]["name"],
                        provider_city_name=str("{},{}").format(
                            hotel.city, hotel.postal_code)
                    )
                    print("its been added")
