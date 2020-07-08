# Generated by Django 3.0.6 on 2020-06-26 07:42

from django.db import migrations

from api.auth.models import Organization

GROUP_NAME = "api-anonymous-users"


def apply_migration(_, schema_editor):
    db_alias = schema_editor.connection.alias

    anonymous = Organization(name="anonymous", active=True, api_burst_limit=5, api_daily_limit=100)
    simplenight = Organization(name="simplenight", active=True, api_burst_limit=100, api_daily_limit=999999)
    Organization.objects.using(db_alias).bulk_create([anonymous, simplenight])


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_organization_organizationapikey'),
    ]

    operations = [migrations.RunPython(apply_migration)]
