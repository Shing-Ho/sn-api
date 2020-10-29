# Generated by Django 3.1.2 on 2020-10-27 04:18

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_auto_20201022_0206'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderChain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_code', models.TextField()),
                ('chain_name', models.TextField()),
                ('modified_date', models.DateTimeField(default=datetime.datetime.now)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.provider')),
            ],
            options={
                'db_table': 'provider_chains',
            },
        ),
        migrations.AddIndex(
            model_name='providerchain',
            index=models.Index(fields=['provider', 'provider_code'], name='provider_ch_provide_e0430a_idx'),
        ),
    ]