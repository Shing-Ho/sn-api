# Generated by Django 3.1.2 on 2020-12-16 07:19

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("api", "0062_searchevent_request_id"),
    ]

    operations = [migrations.RunSQL("CREATE INDEX CONCURRENTLY ON search_events(request_id)")]