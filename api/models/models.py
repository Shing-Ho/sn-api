from django.db import models, connection
from django.contrib.postgres.fields import ArrayField


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
    rating = models.FloatField(blank=True)
    chain_name = models.CharField(max_length=50)
    country_name = models.CharField(max_length=50)
    destination_name = models.CharField(max_length=50)
    address = models.CharField(max_length=75)
    postal_code = models.CharField(max_length=10, null=True)
    city = models.CharField(max_length=50)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    state = models.CharField(max_length=2, default="XX")
    provider_name = models.CharField(max_length=50, default="HotelBeds")


# 'ICEID (don't change)', 'Property Name', 'Country', 'State', 'City',
#     'Address', 'Address2', 'Address3', 'ZipCode', 'Published', 'DID',
#     'MType Id', 'Chain Code', 'Mapped ID'],

# class ice_hotels(models.Model):


class sn_hotel_map(models.Model):
    class Meta:
        app_label = "api"
    simplenight_id = models.IntegerField()
    provider = models.CharField(max_length=50)
    provider_id = models.IntegerField()


class sn_city_map(models.Model):
    class Meta:
        app_label = "api"
    simplenight_city_id = models.IntegerField()
    provider = models.CharField(max_length=50)
    provider_city_name = models.CharField(max_length=50)


class sn_images_map(models.Model):
    class Meta:
        app_label = "api"
    #simplenight_id = models.ForeignKey((supplier_hotels,))
    # on_delete.CASCADE: when object is deleted, delete all references to the object
    simplenight_id = models.CharField(max_length=100, blank=True, null=True)
    image_type = models.TextField(null=True, blank=True)
    image_url_path = models.TextField(null=True, blank=True)
    image_provider_id = models.CharField(max_length=100)
