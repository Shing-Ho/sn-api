
from django.core.management import BaseCommand
from api.models.models import supplier_hotels, sn_hotel_map
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):

        hotels = pd.read_csv("api/FullHotelBedsInventory.csv")
        hotels = hotels[hotels["Country Name"] ==
                        "United Kingdom                          "]

        # print(hotels.columns)

        data = supplier_hotels.objects.all()
        for x in data:
            count = sn_hotel_map.objects.filter(
                provider_id=x.hotel_codes).count()
            if count > 1:
                print(data.hotel_name)

        # for x in range(0, len(hotels)):
        #     try:
        #         if "HALF" in (str(hotels.iloc[x]['Category Name']).replace("STARS", "")):
        #             rating = int(
        #                 str(str(hotels.iloc[x]['Category Name']).replace("STARS", "").replace("AND A HALF", "")))+.5
        #         else:
        #             rating = int(
        #                 str(hotels.iloc[x]['Category Name']).replace("STARS", ""))
        #     except:
        #         pass
        #     try:
        #         c = hotels.iloc[x]['City'].strip()
        #         add = hotels.iloc[x]['Address'].strip()
        #         country = hotels.iloc[x]['Country Name'].strip()
        #         print(c.lower())
        #         print(add.lower())
        #         print(country.lower())
        #         supplier_hotels.objects.update_or_create(
        #             provider_id=0,
        #             hotel_codes=hotels.iloc[x]['Hotel Code'],
        #             hotel_name=hotels.iloc[x]['Hotel Name'].strip(),
        #             rating=rating,
        #             chain_name=hotels.iloc[x]['Chain Name'].strip(),
        #             country_name=country.lower(),
        #             destination_name=hotels.iloc[x]['Destination Name'].strip(
        #             ),
        #             address=add.lower(),
        #             postal_code=hotels.iloc[x]['Postal Code'],
        #             city=c.lower()
        #         )
        #     except:
        #         print("something went wrong with {}".format(
        #             hotels.iloc[x]['Hotel Code']))


# LIST OF HOTELS FROM PROVIDER
