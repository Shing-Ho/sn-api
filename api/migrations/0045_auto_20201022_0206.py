# Generated by Django 3.1.2 on 2020-10-22 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_auto_20201021_0509'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotelbooking',
            name='checkin',
            field=models.DateField(default='1900-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hotelbooking',
            name='checkout',
            field=models.DateField(default='1900-01-01'),
            preserve_default=False,
        ),
    ]
