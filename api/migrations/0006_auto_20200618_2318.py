# Generated by Django 3.0.6 on 2020-06-18 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200618_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mappingcodes',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='mappingcodes',
            name='longitude',
            field=models.FloatField(),
        ),
    ]
