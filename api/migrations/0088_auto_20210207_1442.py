# Generated by Django 3.1.2 on 2021-02-07 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0087_auto_20210203_2039"),
    ]

    operations = [
        migrations.RenameField(
            model_name="productshotelroomdetails",
            old_name="product_hotels",
            new_name="product",
        ),
        migrations.RenameField(
            model_name="productshotelroompricing",
            old_name="product_hotels",
            new_name="product",
        ),
        migrations.AlterField(
            model_name="venuemedia",
            name="url",
            field=models.FileField(upload_to=""),
        ),
    ]
