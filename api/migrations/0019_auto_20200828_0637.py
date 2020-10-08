# Generated by Django 3.0.6 on 2020-08-28 06:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_auto_20200827_0703'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='organization',
            table='organization',
        ),
        migrations.AlterModelTable(
            name='organizationapikey',
            table='organization_api_keys',
        ),
        migrations.CreateModel(
            name='OrganizationFeatures',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(unique=True)),
                ('value', models.TextField()),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='org', to='api.Organization')),
            ],
            options={
                'db_table': 'organization_features',
            },
        ),
    ]