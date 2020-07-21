# Generated by Django 3.0.6 on 2020-07-21 08:12

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_pmt_transaction"),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("booking_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("transaction_id", models.TextField()),
                ("booking_date", models.DateTimeField(auto_now_add=True)),
                (
                    "booking_status",
                    models.CharField(
                        choices=[("booked", "booked"), ("cancelled", "cancelled"), ("pending", "pending")],
                        max_length=32,
                    ),
                ),
            ],
            options={"db_table": "bookings"},
        ),
        migrations.CreateModel(
            name="Traveler",
            fields=[
                (
                    "traveler_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("first_name", models.TextField()),
                ("last_name", models.TextField()),
                ("email_address", models.TextField()),
                ("phone_number", models.TextField()),
                ("city", models.TextField(null=True)),
                ("province", models.TextField(null=True)),
                ("country", models.CharField(max_length=2, null=True)),
                ("address_line_1", models.TextField(null=True)),
                ("address_line_2", models.TextField(null=True)),
            ],
            options={"db_table": "traveler"},
        ),
        migrations.CreateModel(
            name="HotelBooking",
            fields=[
                (
                    "hotel_booking_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("hotel_name", models.TextField()),
                ("crs_name", models.TextField()),
                ("hotel_code", models.TextField()),
                ("record_locator", models.TextField()),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("currency", models.CharField(max_length=3)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.Booking")),
            ],
            options={"db_table": "hotel_bookings"},
        ),
        migrations.AddField(
            model_name="booking",
            name="lead_traveler",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.Traveler"),
        ),
    ]
