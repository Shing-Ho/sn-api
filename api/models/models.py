from django.db import models, connection


USD = 'US Dollars'
FRA = 'French Francs'
ENG = 'English'


class Geoname(models.Model):
    class Meta:
        app_label = "api"

    geoname_id = models.IntegerField(unique=True)
    iso_country_code = models.CharField(max_length=2)
    location_name = models.TextField()
    latitude = models.DecimalField(decimal_places=6, max_digits=11)
    longitude = models.DecimalField(decimal_places=6, max_digits=10)


class GeonameAlternateName(models.Model):
    class Meta:
        app_label = "api"

    alternate_name_id = models.IntegerField()
    iso_language_code = models.CharField(max_length=2)
    name = models.TextField()
    is_colloquial = models.BooleanField()
    iatacode = models.CharField(max_length=3)

    geoname = models.ForeignKey(
        Geoname, to_field="geoname_id", on_delete=models.CASCADE, null=True, related_name="lang"
    )


class bookingrequest(models.Model):

    class Meta:
        app_label = "api"

    currency_list = [(USD, 'US DOLLARS'), ]
    language_list = [(ENG, 'ENGLISH'), ]
    # userid = models.CharField(max_length=30)
    checkindate = models.DateField(auto_now=True)
    checkoutdate = models.DateField(auto_now=True)
    currency = models.CharField(
        max_length=30, choices=currency_list, default=USD)
    language = models.CharField(
        max_length=10, choices=language_list, default=USD)
    occupancy = models.IntegerField(1, default=1)
    snpropertyid = models.CharField(max_length=10, default="AAA")  # <--
    package = models.BooleanField(default=False)  # <--
    Standalone = models.BooleanField(default=True)


class supplier_hotels(models.Model):

    class Meta:
        app_label = "api"

    provider_id = models.IntegerField()
    hotel_codes = models.IntegerField(default=1)
    hotel_name = models.CharField(max_length=50)
    rating = models.supplier_hotelsloatField(blank=True)
    chain_name = models.CharField(max_length=50)
    country_name = models.CharField(max_length=50)
    destination_name = models.CharField(max_length=50)
    address = models.CharField(max_length=75)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()


# class sn_hotel_map(): <--- we cant leave this empty we must use models.Model for example
    # if we dont have it we dont have access to .objects etc
#     class Meta: app_label = "api" this must be added in because models does doesnt recognize what app it is
#     simplenight_id = models.IntegerField(5)
#     provider = models.CharField(max_length=50)
#     provider_id = models.IntegerField(5) <----- we dont want to put this 5 in there it doesnt do
#                                               anything other than displace the field
#                                               as a 5 instead of provider_id

class sn_hotel_map(models.Model):
    class Meta:
        app_label = "api"
    simplenight_id = models.IntegerField()
    provider = models.CharField(max_length=50)
    provider_id = models.IntegerField()
