# Generated by Django 3.1.2 on 2020-11-01 03:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0052_auto_20201030_0627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotelcancellationpolicy',
            name='penalty_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.CreateModel(
            name='PropertyInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_code', models.TextField()),
                ('type', models.TextField()),
                ('language_code', models.CharField(max_length=2)),
                ('description', models.TextField()),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.provider')),
            ],
            options={
                'db_table': 'property_info',
            },
        ),
        migrations.AddIndex(
            model_name='propertyinfo',
            index=models.Index(fields=['provider', 'provider_code', 'language_code', 'type'], name='property_in_provide_184978_idx'),
        ),
    ]
