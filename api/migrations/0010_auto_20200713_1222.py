# Generated by Django 3.0.6 on 2020-07-13 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20200713_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sn_images_map',
            name='image_type',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sn_images_map',
            name='image_url_path',
            field=models.TextField(blank=True, null=True),
        ),
    ]
