# Generated by Django 3.1.2 on 2020-10-19 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20201014_0708'),
    ]

    operations = [
        migrations.AddField(
            model_name='providerhotel',
            name='provider_reference',
            field=models.TextField(null=True),
        ),
    ]
