# Generated by Django 3.1.2 on 2021-02-11 06:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0089_auto_20210211_0623"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="booking_status",
            field=models.CharField(
                choices=[
                    ("booked", "booked"),
                    ("cancelled", "cancelled"),
                    ("pending", "pending"),
                    ("failed", "failed"),
                ],
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="ActivityBookingModel",
            fields=[
                (
                    "activity_reservation_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("activity_name", models.TextField()),
                ("activity_code", models.TextField()),
                ("activity_date", models.DateField()),
                ("activity_time", models.TextField(null=True)),
                ("thumbnail", models.TextField(null=True)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=7)),
                ("total_taxes", models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ("total_base", models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ("provider_price", models.DecimalField(decimal_places=2, max_digits=7)),
                ("provider_taxes", models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ("provider_base", models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ("currency", models.CharField(max_length=3)),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_reservation",
                        to="api.booking",
                    ),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="provider", to="api.provider"
                    ),
                ),
            ],
            options={"db_table": "activity_reservations"},
        ),
        migrations.CreateModel(
            name="ActivityBookingItemModel",
            fields=[
                (
                    "activity_reservation_item_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("item_code", models.TextField()),
                ("quantity", models.IntegerField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "activity_reservation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_reservation",
                        to="api.activitybookingmodel",
                    ),
                ),
            ],
            options={"db_table": "activity_reservation_items"},
        ),
    ]
