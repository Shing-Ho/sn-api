# Generated by Django 3.0.6 on 2020-09-28 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_auto_20200928_1201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cancelationbookingpolicy',
            old_name='hotel_booking',
            new_name='booking',
        ),
        migrations.AlterField(
            model_name='cancelationbookingpolicy',
            name='cancelable_hours',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='cancelationbookingpolicy',
            name='refundable_amount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
