# Generated by Django 3.1.2 on 2021-02-03 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0086_auto_20210203_2022"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producthotelsmedia",
            name="url",
            field=models.FileField(blank=True, null=True, upload_to=""),
        ),
        migrations.AlterField(
            model_name="productsnightlifemedia",
            name="url",
            field=models.FileField(blank=True, null=True, upload_to=""),
        ),
    ]
