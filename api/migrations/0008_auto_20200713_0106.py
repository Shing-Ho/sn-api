# Generated by Django 3.0.6 on 2020-07-13 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_sn_images_map_provider_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sn_images_map',
            old_name='ip_thumbnail_image',
            new_name='image_type',
        ),
        migrations.RemoveField(
            model_name='sn_images_map',
            name='provider_id',
        ),
        migrations.AlterField(
            model_name='sn_images_map',
            name='simplenight_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
