from django.core.management import BaseCommand
from api.models.models import supplier_hotels
import pandas as pd
from api.models.models import supplier_hotels, sn_hotel_map, hotel_listing


class Command(BaseCommand):

    '''
    Just to test data

    'provider', 'hotelid', 'hotelname',
       'zipcode', 'stars', 'countrycode', 'address', 'city_names', 'street',
       'sn_id', 'new_string'],
    '''

    def handle(self, *args, **options):
        main_data = pd.read_csv(r"C:\Users\tony\Downloads\with_iceportal.csv")
        print(hotel_listing.objects.all().count())
