
from django.core.management import BaseCommand
from api.models.models import supplier_hotels
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):

        hotels = pd.read_csv("api/FullHotelBedsInventory.csv")

        print(hotels.columns)

        for x in range(0, len(hotels)):
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
                supplier_hotels.objects.update_or_create(
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


# LIST OF HOTELS FROM PROVIDER
