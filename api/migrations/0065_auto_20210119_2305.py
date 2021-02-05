# Generated by Django 3.1.2 on 2021-01-19 23:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0064_add_search_event_index_created_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="Venue",
            fields=[
                ("venue_id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=32, unique=True)),
                ("venue_from", models.CharField(choices=[("SN", "SN"), ("PO", "PO")], default="SN", max_length=2)),
                (
                    "venue_type",
                    models.CharField(
                        choices=[
                            ("NIGHT_LIFE", "NIGHT_LIFE"),
                            ("CAR_SERVICE", "CAR_SERVICE"),
                            ("GAS_AND_CHARGING", "GAS_AND_CHARGING"),
                            ("TOLLS", "TOLLS"),
                            ("SHOPPINGS", "SHOPPINGS"),
                            ("THINGS_TO_DO", "THINGS_TO_DO"),
                            ("DINING", "DINING"),
                            ("FAST_FOOD", "FAST_FOOD"),
                            ("COFFEE_AND_TEA", "COFFEE_AND_TEA"),
                        ],
                        default="NIGHT_LIFE",
                        max_length=20,
                    ),
                ),
                ("language_code", models.CharField(default="en", max_length=3)),
                ("tags", models.CharField(blank=True, max_length=100, null=True)),
                ("rating", models.IntegerField(blank=True, null=True)),
                ("status", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="venue_requests_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="venue_requests_modified",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name": "Venue", "verbose_name_plural": "Venues",},
        ),
    ]
