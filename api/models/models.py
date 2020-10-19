#!/usr/bin/env python
import uuid
from enum import Enum, EnumMeta
from typing import Tuple, List

from django.contrib.postgres.fields import ArrayField
from django.db import models

from api.hotel.hotel_api_model import CancellationSummary


def choices(cls: EnumMeta) -> List[Tuple]:
    return [(x.value, x.value) for x in cls]


class Geoname(models.Model):
    class Meta:
        app_label = "api"
        indexes = [
            models.Index(fields=["location_name"]),
        ]

    geoname_id = models.IntegerField(unique=True)
    iso_country_code = models.CharField(max_length=2)
    province = models.CharField(max_length=20)
    location_name = models.TextField()
    latitude = models.DecimalField(decimal_places=6, max_digits=11)
    longitude = models.DecimalField(decimal_places=6, max_digits=10)
    timezone = models.CharField(max_length=40)
    population = models.IntegerField()


class GeonameAlternateName(models.Model):
    class Meta:
        app_label = "api"
        indexes = [
            models.Index(fields=["name"]),
        ]

    alternate_name_id = models.IntegerField()
    iso_language_code = models.CharField(max_length=2)
    name = models.TextField()
    is_colloquial = models.BooleanField()
    iatacode = models.CharField(max_length=3)

    geoname = models.ForeignKey(
        Geoname, to_field="geoname_id", on_delete=models.CASCADE, null=True, related_name="lang"
    )


class Airport(models.Model):
    class Meta:
        app_label = "api"
        db_table = "airports"
        indexes = [
            models.Index(fields=["airport_name", "airport_code"]),
        ]

    airport_id = models.IntegerField()
    airport_name = models.TextField()
    city_name = models.TextField()
    iso_country_code = models.TextField()
    airport_code = models.CharField(max_length=3)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezone = models.TextField()
    geoname = models.ForeignKey(
        Geoname, to_field="geoname_id", related_name="geoname", null=True, on_delete=models.SET_NULL
    )


def default_uuid_8():
    return str(uuid.uuid4())[:8]


def default_uuid_12():
    return str(uuid.uuid4())[-12:]


class Provider(models.Model):
    class Meta:
        app_label = "api"
        db_table = "providers"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)


class ProviderCity(models.Model):
    class Meta:
        app_label = "api"
        db_table = "provider_cities"

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_code = models.TextField(unique=True)
    location_name = models.TextField()
    province = models.TextField()
    country_code = models.CharField(max_length=2)
    latitude = models.DecimalField(decimal_places=6, max_digits=11)
    longitude = models.DecimalField(decimal_places=6, max_digits=11)


class CityMap(models.Model):
    class Meta:
        app_label = "api"

    id = models.AutoField(primary_key=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    simplenight_city = models.ForeignKey(
        Geoname, to_field="geoname_id", related_name="simplenight_city", on_delete=models.CASCADE
    )
    provider_city = models.ForeignKey(
        ProviderCity, to_field="provider_code", related_name="provider_city", on_delete=models.CASCADE
    )


class supplier_priceline(models.Model):
    class Meta:
        app_label = "api"
        indexes = [
            models.Index(fields=["hotelid_ppn"]),
        ]

    supplier = models.CharField(max_length=50, default="Priceline")
    supplier_id = models.CharField(max_length=100, blank=True, null=False)
    hotel_name = models.CharField(max_length=100)
    hotel_address = models.CharField(max_length=100)
    hotel_city = models.CharField(max_length=100)
    hotel_state = models.CharField(max_length=25)
    hotel_country_code = models.CharField(max_length=3)
    hotel_postal_code = models.CharField(max_length=15)
    hotel_rating = models.FloatField()
    hotel_description = models.TextField(max_length=100)
    hotel_amenities = ArrayField(ArrayField(models.CharField(max_length=100, blank=True), size=8,), size=8,)
    hotelid_ppn = models.TextField(max_length=100)
    cityid_ppn = models.TextField(max_length=100)
    image_url_path = models.TextField(null=True, blank=True)


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
    provider_name = models.TextField()
    hotel_code = models.TextField()
    record_locator = models.TextField()
    total_price = models.DecimalField(decimal_places=2, max_digits=8)
    currency = models.CharField(max_length=3)
    provider_total = models.DecimalField(decimal_places=2, max_digits=8)
    provider_currency = models.CharField(max_length=3)


class HotelCancellationPolicy(models.Model):
    class Meta:
        app_label = "api"
        db_table = "api_hotel_cancellation_policy"

    cancellation_policy_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    hotel_booking = models.ForeignKey(HotelBooking, on_delete=models.CASCADE)
    cancellation_type = models.TextField(choices=choices(CancellationSummary))
    description = models.TextField(null=True)
    begin_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    penalty_amount = models.DecimalField(decimal_places=2, max_digits=8, null=True)
    penalty_currency = models.CharField(max_length=3, null=True)


class ProviderMapping(models.Model):
    class Meta:
        app_label = "api"
        db_table = "provider_mappings"
        indexes = [
            models.Index(fields=["provider", "provider_code"]),
            models.Index(fields=["provider", "giata_code"]),
        ]

    provider_mapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    giata_code = models.TextField()
    provider_code = models.TextField()


class ProviderImages(models.Model):
    class Meta:
        app_label = "api"
        db_table = "provider_images"
        indexes = [
            models.Index(fields=["provider", "provider_code"]),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_code = models.TextField()
    type = models.TextField()
    display_order = models.IntegerField()
    image_url = models.TextField()


class ProviderHotel(models.Model):
    class Meta:
        app_label = "api"
        db_table = "provider_hotel"
        indexes = [
            models.Index(fields=["provider", "provider_code"]),
        ]

    provider_hotel_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_code = models.TextField()
    language_code = models.CharField(max_length=2, default="en")
    hotel_name = models.TextField()
    city_name = models.TextField(null=True)
    state = models.TextField(null=True)
    country_code = models.CharField(max_length=2, null=True)
    address_line_1 = models.TextField(null=True)
    address_line_2 = models.TextField(null=True)
    postal_code = models.CharField(max_length=10, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
