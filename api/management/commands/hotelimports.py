
from django.core.management import BaseCommand
from api.models.models import mappingcodes
import pandas as pd

class Command(BaseCommand):
    def handle(self, *args, **options):


        #hotels = pd.read_csv("api/FullHotelBedsInventory.csv")
        '''
        print(hotels.columns)
        for x in range(0, len(hotels)):
            try:

                mappingcodes.objects.update_or_create(
                    provider_id=0,
                    hotel_codes=hotels.iloc[x]['Hotel Code'],
                    hotel_name=hotels.iloc[x]['Hotel Name'],
                    category_name=hotels.iloc[x]['Category Name'],
                    chain_name=hotels.iloc[x]['Chain Name'],
                    country_name=hotels.iloc[x]['Country Name'],
                    destination_name=hotels.iloc[x]['Destination Name'],
                    address=hotels.iloc[x]['Address'],
                    postal_code=hotels.iloc[x]['Postal Code'],
                    city=hotels.iloc[x]['City'],
                    latitude=round(int(str(hotels.iloc[x]['Latitude']
                                           ).replace(",", ""))/100000, 5),
                    longitude=round(int(str(hotels.iloc[x]['Longitude']).replace(
                        ",", ""))/100000, 5)
                )
            except:
                print("had a nan")


['Hotel Code', 'Hotel Name', 'Category Name', 'Chain Name',
       'Country Name', 'Destination Name', 'Address', 'Postal Code', 'City',
       'Latitude', 'Longitude'],
    
    provider_id = models.IntegerField(5)
    hotel_codes = models.IntegerField(1, default=1)
    hotel_name = models.CharField(max_length=50)
    category_name = models.CharField(max_length=20, blank = True)
    chain_name = models.CharField(max_length=50)
    country_name = models.CharField(max_length=50)
    destination_name = models.CharF"ield(max_length=50)
    address = models.CharField(max_length=75)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    latitude = models.DecimalField(decimal_places=6, max_digits=11)
    longitude = models.DecimalField(decimal_places=6, max_digits=10)
'''
