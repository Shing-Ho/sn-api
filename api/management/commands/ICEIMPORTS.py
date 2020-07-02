from django.core.management import BaseCommand
from api.models.models import supplier_hotels
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):

        hotels = pd.read_csv("iceportaldata.csv")

        print(hotels.columns)

        for x in range(0, 1025):  # len(hotels)):

            supplier_hotels.objects.update_or_create(
                provider_id=hotels.iloc[x]["ICEID (don't change)"],
                hotel_codes=hotels.iloc[x]["ICEID (don't change)"],
                hotel_name=str(
                    hotels.iloc[x]['Property Name']).replace(" ", ""),
                rating=0,
                chain_name=hotels.iloc[x]['Chain Code'],
                country_name=hotels.iloc[x]['Country'],
                destination_name=str(
                    hotels.iloc[x]['Property Name']).replace(" ", ""),
                address=hotels.iloc[x]['Address'],
                postal_code=hotels.iloc[x]['ZipCode'],
                city=str(hotels.iloc[x]['City']).replace(" ", ""),
                provider_name="Ice Portal"
            )
