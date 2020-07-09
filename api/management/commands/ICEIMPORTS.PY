from django.core.management import BaseCommand
from api.models.models import supplier_hotels
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
        supplier_hotels.objects.all().delete()
        hotels = pd.read_csv("iceportaldata.csv")
        hotels = hotels[hotels['Country'] == "United Kingdom"]

        print(len(hotels))

        for x in range(0, len(hotels)):
            try:
                c = hotels.iloc[x]['City'].strip()
                add = hotels.iloc[x]['Address'].strip()
                country = hotels.iloc[x]['Country'].strip()
                print(c.lower())
                print(add.lower())
                print(country.lower())
                supplier_hotels.objects.update_or_create(
                    provider_id=hotels.iloc[x]["ICEID (don't change)"],
                    hotel_codes=hotels.iloc[x]["ICEID (don't change)"],
                    hotel_name=hotels.iloc[x]['Property Name'].strip(),
                    rating=0,
                    chain_name=hotels.iloc[x]['Chain Code'],
                    country_name=country.lower(),
                    destination_name=hotels.iloc[x]['Property Name'].strip(
                    ),
                    address=a.lower(),
                    postal_code=hotels.iloc[x]['ZipCode'],
                    city=c.lower(),
                    provider_name="Ice Portal"
                )
            except:
                print(len(str(
                    hotels.iloc[x]['Property Name']).replace(" ", "")))
