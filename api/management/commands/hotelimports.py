
from django.core.management import BaseCommand
from api.models.models import supplier_hotels, sn_hotel_map, hotel_listing
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):

        main_data = pd.read_csv(r"C:\Users\tony\Downloads\with_iceportal.csv")
        print(main_data.head())
        stars = ['3', '0', '4', '2', '6', '1', '5', '3.5', '2.5', '4.5', '1.5', '5.5']
        main_data["stars"] = main_data.stars.str.replace("+", ".5")
        main_data["stars"] = main_data.stars.str.replace(" ", "")
        main_data["stars"] = main_data.stars.str.replace("ANDAHALF", ".5")
        main_data["stars"] = main_data.stars.str.replace("star", "")
        main_data["stars"] = main_data.stars.str.replace("LUXURY", "")
        main_data["stars"] = main_data.stars.str.replace(" ", "0")

        # main_data = main_data[main_data.isin(stars)]
        # main_data["stars"] = main_data["stars"].astype("float64")

        print(main_data["stars"].value_counts())
        # print(main_data["stars"].value_counts().index)
        for i in range(0, len(main_data)):
            if i in [100, 1000, 20000, 100000, 200000, 400000]:
                print(i)
            try:
                stars = int(main_data.iloc[i]["stars"])
            except:
                stars = 0
            hotel_listing.objects.update_or_create(
                provider=main_data.iloc[i]["provider"],
                simplenight_id=main_data.iloc[i]["sn_id"],
                address=main_data.iloc[i]["address"],
                city=main_data.iloc[i]["city_names"],
                hotelid=main_data.iloc[i]["hotelid"],
                zipcode=main_data.iloc[i]["zipcode"],
                stars=stars,
                countrycode=main_data.iloc[i]["countrycode"]
            )
            # except:
            # print(main_data.iloc[i])
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
