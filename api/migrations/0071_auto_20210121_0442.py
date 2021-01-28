# Generated by Django 3.1.2 on 2021-01-21 04:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0070_venuecontacts'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('icon', models.TextField(blank=True, null=True)),
                ('api_key', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'PaymentMethod',
                'verbose_name_plural': 'PaymentMethods',
                'db_table': 'payment_methods',
            },
        ),
        migrations.AlterField(
            model_name='venue',
            name='name',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]
