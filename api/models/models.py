#!/usr/bin/env python
import uuid
from enum import Enum

import stripe
from django.db import models

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

USD = "US Dollars"
FRA = "French Francs"
ENG = "English"


class Geoname(models.Model):
    class Meta:
        app_label = "api"

    geoname_id = models.IntegerField(unique=True)
    iso_country_code = models.CharField(max_length=2)
    province_code = models.CharField(max_length=20)
    location_name = models.TextField()
    latitude = models.DecimalField(decimal_places=6, max_digits=11)
    longitude = models.DecimalField(decimal_places=6, max_digits=10)
    timezone = models.CharField(max_length=40)
    population = models.IntegerField()


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


class hotel_listing(models.Model):
    class Meta:
        app_label = "api"

    provider = models.TextField(null=True, blank=True)
    hotelid = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    hotelname = models.TextField(null=True, blank=True)
    zipcode = models.TextField(null=True, blank=True)
    stars = models.FloatField(null=True, blank=True)
    countrycode = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    simplenight_id = models.IntegerField(null=True)

    def image(self):
        try:
            image = sn_images_map.objects.filter(simplenight_id=self.hotelid).image_url_path

        except:
            image = None

        return image

    # def images():
    #     images = []
    #     for item in images.objects.filter(this="that"):
    #         images.append(item.image_url_path)
    #     return images


def default_uuid_8():
    return str(uuid.uuid4())[:8]


def default_uuid_12():
    return str(uuid.uuid4())[-12:]


class Provider(models.Model):
    class Meta:
        app_label = "api"
        db_table = "providers"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)


class CrsCity(models.Model):
    class Meta:
        app_label = "api"
        db_table = "crs_cities"

    id = models.AutoField(primary_key=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_code = models.TextField()
    location_name = models.TextField()
    province_code = models.TextField()
    country_code = models.CharField(max_length=2)
    latitude = models.DecimalField(decimal_places=6, max_digits=11)
    longitude = models.DecimalField(decimal_places=6, max_digits=11)


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

    # simplenight_id = models.ForeignKey((supplier_hotels,))
    # on_delete.CASCADE: when object is deleted, delete all references to the object
    simplenight_id = models.CharField(max_length=100, blank=True, null=True)
    image_type = models.TextField(null=True, blank=True)
    image_url_path = models.TextField(null=True, blank=True)
    image_provider_id = models.CharField(max_length=100)


class PaymentTransaction(models.Model):
    class Meta:
        app_label = "api"
        db_table = "pmt_transaction"

    sn_transaction_id = models.IntegerField(null=True)
    provider_name = models.CharField(max_length=32)
    charge_id = models.CharField(max_length=50)
    transaction_type = models.CharField(max_length=12)
    transaction_status = models.CharField(max_length=50)
    transaction_amount = models.FloatField()
    currency = models.CharField(max_length=3)
    transaction_time = models.DateTimeField(auto_now_add=True)
    payment_token = models.CharField(max_length=128)


class Traveler(models.Model):
    class Meta:
        app_label = "api"
        db_table = "api_traveler"

    traveler_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.TextField()
    last_name = models.TextField()
    email_address = models.TextField()
    phone_number = models.TextField()
    city = models.TextField(null=True)
    province = models.TextField(null=True)
    country = models.CharField(max_length=2, null=True)
    address_line_1 = models.TextField(null=True)
    address_line_2 = models.TextField(null=True)


class BookingStatus(Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    PENDING = "pending"


class Booking(models.Model):
    class Meta:
        app_label = "api"
        db_table = "api_bookings"

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.TextField()
    booking_date = models.DateTimeField(auto_now_add=True)
    booking_status = models.CharField(max_length=32, choices=[(x.value, x.value) for x in BookingStatus])
    lead_traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)


class HotelBooking(models.Model):
    class Meta:
        app_label = "api"
        db_table = "api_hotel_bookings"

    hotel_booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    hotel_name = models.TextField()
    crs_name = models.TextField()
    hotel_code = models.TextField()
    record_locator = models.TextField()
    total_price = models.DecimalField(decimal_places=2, max_digits=8)
    currency = models.CharField(max_length=3)
    crs_total_price = models.DecimalField(decimal_places=2, max_digits=8)
    crs_currency = models.CharField(max_length=3)


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
    state = models.CharField(max_length=2, default="X")
    provider_name = models.CharField(max_length=50, default="HotelBeds")
