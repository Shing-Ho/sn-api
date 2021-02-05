# Generated by Django 3.1.2 on 2021-01-21 06:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0072_auto_20210121_0606"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venuedetail",
            name="payment_method",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="venuedetail_requests_modified",
                to="api.paymentmethod",
            ),
        ),
    ]
