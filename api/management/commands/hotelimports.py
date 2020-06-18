
from django.core.management import BaseCommand
from api.models.models import mappingcodes
import pandas as pd

class Command(BaseCommand):
    def handle(self,*args,**options):
        hotels = pd.read_csv("api/FullHotelBedsInventory.csv")
        print(hotels.columns)

'''
    
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