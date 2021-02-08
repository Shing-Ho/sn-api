# Generated by Django 3.1.2 on 2021-02-03 20:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0085_auto_20210126_0955"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductHotelsMedia",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "type",
                    models.CharField(
                        blank=True, choices=[("VIDEO", "VIDEO"), ("IMAGE", "IMAGE")], max_length=8, null=True
                    ),
                ),
                ("url", models.TextField(blank=True, null=True)),
                ("thumbnail", models.TextField()),
                ("main", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "ProductHotelMedia",
                "verbose_name_plural": "ProductHotelMedia",
                "db_table": "products_hotels_media",
            },
        ),
        migrations.CreateModel(
            name="ProductsNightLifeMedia",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "type",
                    models.CharField(
                        blank=True, choices=[("VIDEO", "VIDEO"), ("IMAGE", "IMAGE")], max_length=8, null=True
                    ),
                ),
                ("url", models.TextField(blank=True, null=True)),
                ("thumbnail", models.TextField()),
                ("main", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="media",
                        to="api.productsnightlife",
                    ),
                ),
                ("venue", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.venue")),
            ],
            options={
                "verbose_name": "ProductsNightLifeMedia",
                "verbose_name_plural": "ProductsNightLifeMedia",
                "db_table": "products_nightlife_media",
            },
        ),
        migrations.RenameModel(
            old_name="ProductHotels",
            new_name="ProductHotel",
        ),
        migrations.DeleteModel(
            name="ProductMedia",
        ),
        migrations.AddField(
            model_name="producthotelsmedia",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_hotels",
                to="api.producthotel",
            ),
        ),
        migrations.AddField(
            model_name="producthotelsmedia",
            name="venue",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.venue"),
        ),
    ]
