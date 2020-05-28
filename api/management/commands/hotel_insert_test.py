
import requests
from requests.auth import HTTPBasicAuth
import time
from django.core.management.base import BaseCommand, CommandError
from api.models.models import Hotels
import json

class Command(BaseCommand):



    def handle(self, *args, **options):
        Hotels.objects.create(name="Motel 8",city="New York City",stars=4)
        Hotels.objects.create(name="Four Seasons",city="New York City",stars=1)
        Hotels.objects.create(name="Holiday Inn",city="Hartford",stars=5)
        Hotels.objects.create(name="Days Inn",city="Worcester",stars=4)
