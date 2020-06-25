
from django.core.management import BaseCommand
from api.models.models import hotelmappingcodes
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        hotelmappingcodes.objects.all().delete()

        hotels = pd.read_csv("api/FullHotelBedsInventory.csv")

        print(hotels.columns)

        for x in range(0, 1111):
            try:
                if "HALF" in (str(hotels.iloc[x]['Category Name']).replace("STARS", "")):
                    rating = int(
                        str(str(hotels.iloc[x]['Category Name']).replace("STARS", "").replace("AND A HALF", "")))+.5
                else:
                    rating = int(
                        str(hotels.iloc[x]['Category Name']).replace("STARS", ""))
            except:
                pass
            try:
                hotelmappingcodes.objects.update_or_create(
                    provider_id=0,
                    hotel_codes=hotels.iloc[x]['Hotel Code'],
                    hotel_name=str(
                        hotels.iloc[x]['Hotel Name']).replace(" ", ""),
                    rating=rating,
                    chain_name=hotels.iloc[x]['Chain Name'].strip(),
                    country_name=hotels.iloc[x]['Country Name'],
                    destination_name=str(
                        hotels.iloc[x]['Destination Name']).replace(" ", ""),
                    address=hotels.iloc[x]['Address'],
                    postal_code=hotels.iloc[x]['Postal Code'],
                    city=str(hotels.iloc[x]['City']).replace(" ", ""),
                    latitude=round(int(str(hotels.iloc[x]['Latitude']
                                           ).replace(",", ""))/100000, 5),
                    longitude=round(int(str(hotels.iloc[x]['Longitude']).replace(
                        ",", ""))/1000000, 5)
                )
            except:
                print("")


'''
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
