# Generated by Django 3.1.2 on 2021-02-10 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0089_auto_20210209_2114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venue",
            name="name",
            field=models.CharField(max_length=300),
        ),
    ]
