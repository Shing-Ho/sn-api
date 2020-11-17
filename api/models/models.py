#!/usr/bin/env python
import random
import string
import uuid
from enum import EnumMeta, Enum
from typing import Tuple, List

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django_enumfield import enum

from api import logger
from api.hotel.models.hotel_api_model import CancellationSummary
from api.hotel.models.hotel_common_models import Address, BookingStatus


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
    location_type = models.TextField(null=True)


class GeonameAlternateName(models.Model):
    class Meta:
        app_label = "api"
        indexes = [
            models.Index(fields=["name"]),
        ]

    alternate_name_id = models.IntegerField()
    iso_language_code = models.CharField(max_length=2)
    name = models.TextField()
    is_preferred = models.BooleanField()
    is_short_name = models.BooleanField()
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


class Feature(Enum):
    ENABLED_ADAPTERS = "enabled_connectors"
    TEST_MODE = "test_mode"
    STRIPE_API_KEY = "stripe_api_key"
    PRICELINE_API_URL = "priceline_api_url"
    MAILGUN_API_KEY = "mailgun_api_key"
    EMAIL_ENABLED = "email_enabled"
    HOTELBEDS_API_URL = "hotelbeds_api_url"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Organization(models.Model):
    class Meta:
        app_label = "api"
        db_table = "organization"
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    username = models.CharField(max_length=32, null=True)
    api_daily_limit = models.IntegerField()
    api_burst_limit = models.IntegerField()

    def get_feature(self, feature: Feature):
        try:
            result = OrganizationFeatures.objects.get(organization_id=self.id, name=feature.value)
            return result.value
        except OrganizationFeatures.DoesNotExist:
            return None

    def set_feature(self, feature_type: Feature, value):
        feature_name = feature_type.value
        feature, _ = OrganizationFeatures.objects.get_or_create(organization_id=self.id, name=feature_name)

        feature.value = value
        feature.save()

    def clear_feature(self, feature_type: Feature):
        feature = OrganizationFeatures.objects.get(organization_id=self.id, name=feature_type.value)
        if feature:
            feature.delete()

    def __str__(self):
        return f"{self.name} ({self.id})"


class OrganizationFeatures(models.Model):
    class Meta:
        app_label = "api"
        db_table = "organization_features"
        unique_together = ("organization", "name")
        verbose_name = "Organization Feature"
        verbose_name_plural = "Organization Features"

    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="org")
    name = models.TextField(choices=Feature.choices())
    value = models.TextField()

    def organization_name(self):
        return self.organization.name


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


class Booking(models.Model):
    class Meta:
        app_label = "api"
        db_table = "api_bookings"
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    transaction_id = models.TextField()
    booking_date = models.DateTimeField(auto_now_add=True)
    booking_status = models.CharField(max_length=32, choices=[(x.value, x.value) for x in BookingStatus])
    lead_traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)


class TransactionType(enum.Enum):
    CHARGE = 0
    REFUND = 1


class PaymentTransaction(models.Model):
    class Meta:
        app_label = "api"
        db_table = "payment_transaction"

    sn_transaction_id = models.IntegerField(null=True)
    booking = models.ForeignKey(Booking, null=True, on_delete=models.SET_NULL)
    provider_name = models.CharField(max_length=32)
    charge_id = models.CharField(max_length=50)
    transaction_type = enum.EnumField(TransactionType)
    transaction_status = models.CharField(max_length=50)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    transaction_time = models.DateTimeField(auto_now_add=True)
    payment_token = models.CharField(max_length=128, null=True)


class HotelBooking(models.Model):
    class Meta:
        app_label = "api"
        db_table = "api_hotel_bookings"

    hotel_booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    hotel_name = models.TextField()
    provider = models.ForeignKey(Provider, null=True, on_delete=models.SET_NULL)
    simplenight_hotel_id = models.TextField(null=True)
    provider_hotel_id = models.TextField()
    record_locator = models.TextField()
    total_price = models.DecimalField(decimal_places=2, max_digits=8)
    currency = models.CharField(max_length=3)
    provider_total = models.DecimalField(decimal_places=2, max_digits=8)
    provider_currency = models.CharField(max_length=3)
    checkin = models.DateField()
    checkout = models.DateField()


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
    penalty_amount = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    penalty_currency = models.CharField(max_length=3, null=True)

    def get_cancellation_type(self):
        if not self.cancellation_type:
            return None

        return CancellationSummary.from_value(self.cancellation_type)


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
    postal_code = models.TextField(null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    thumbnail_url = models.TextField(null=True)
    star_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    property_description = models.TextField(blank=True, null=True)
    amenities = ArrayField(models.CharField(max_length=100, blank=True), null=True)
    provider_reference = models.TextField(null=True)

    def get_address(self):
        return Address(
            city=self.city_name,
            province=self.state,
            country=self.country_code,
            address1=self.address_line_1,
            address2=self.address_line_2,
            postal_code=self.postal_code,
        )


class PhoneType(enum.Enum):
    VOICE = 1
    FAX = 2

    @classmethod
    def from_name(cls, value):
        if not value:
            return

        if not hasattr(cls, "name_map"):
            cls.name_map = {x.name.lower(): x for x in PhoneType}

        return cls.name_map.get(value.lower())


class ProviderHotelPhones(models.Model):
    class Meta:
        app_label = "api"
        db_table = "provider_hotel_phones"
        indexes = [
            models.Index(fields=["provider", "provider_code"]),
        ]

    provider_hotel_phone_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    provider_hotel = models.ForeignKey(ProviderHotel, on_delete=models.CASCADE, null=True, related_name="phone")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_code = models.TextField()
    type = enum.EnumField(PhoneType)
    phone_number = models.TextField()


class ProviderChain(models.Model):
    class Meta:
        app_label = "api"
        db_table = "provider_chains"
        indexes = [
            models.Index(fields=["provider", "provider_code"]),
        ]

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_code = models.TextField()
    chain_name = models.TextField()
    modified_date = models.DateTimeField(default=timezone.now)


class RecordLocator(models.Model):
    record_locator = models.CharField(max_length=8)
    booking = models.ForeignKey(to=Booking, on_delete=models.SET_NULL, null=True)

    @classmethod
    def generate_record_locator(cls, booking):
        """
        Generates an 8 digit record locator, ensuring one does not already exist in the DB
        This is the identifier used by customers to find their Simplenight booking
        """
        valid_chars = string.ascii_uppercase + string.digits

        for _ in range(10):
            record_locator = str.join("", (random.choice(valid_chars) for _ in range(8)))
            model, created = RecordLocator.objects.get_or_create(record_locator=record_locator)
            if not created:
                logger.info("Record locator already exists: " + record_locator)
                continue

            model.booking = booking
            model.save()
            return record_locator

        raise RuntimeError("Could not find record locator")


class PropertyInfo(models.Model):
    class Meta:
        app_label = "api"
        db_table = "property_info"
        indexes = [
            models.Index(fields=["provider", "provider_code", "language_code", "type"]),
        ]

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    provider_code = models.TextField()
    type = models.TextField()
    language_code = models.CharField(max_length=2)
    description = models.TextField()
