# -*- coding: utf-8 -*-
#!/usr/bin/env python

from django.core.management import BaseCommand
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport

from api.models.models import sn_images_map
from api.models.models import supplier_hotels


class Command(BaseCommand):
    def handle(self, *args, **options):
        session = Session()
        auth = HTTPBasicAuth("distributor@simplenight.com", "Gp*3eA")
        client = Client("http://services.iceportal.com/Service.asmx?WSDL", transport=Transport(session=session))

        # get list of all properties
        main_dict = {"Ice Portal": {"model": sn_images_map, "name": "Ice Portal"}}
        properties = supplier_hotels.objects.filter(provider_name="Ice Portal")
        for hotel in properties:
            print(hotel.hotel_codes)

        # get list
        # Main image for a particular property plus thumbnail passed to front end from db
        # but we must get the image id from the ui
        """
        main_dict = {"iceportal": {
            "model": sn_images_map, "name": "Ice Portal"}}

        for table in main_dict.keys():
            for hotel in main_dict[table]["model"].objects.all():
                if sn_images_map.objects.filter(provider_id=hotel.hotel_codes).count() > 0:
                    # dont do anything we already have this in the database
                    print("exists...")


        # url(r'url with a value', view.someview, name='image')


        #main_image = sn_images_map.objects.get(params)


        #  pass in the ice id from the property to get that main image
        
       
        if requests.method == 'GET':
        
        if simplenight_city_id = models.ForeignKey((supplier_hotels))
            # simplenight_city_id = models.IntegerField()
            thumbnail_image = ArrayField(ArrayField(models.CharField()))
            url_path = models.CharField(100)
            image_provider_id = models.IntegerField
        
        
        
        #ICEPORTAL_SERVICE_WSDL = getattr(settings, 'ICEPORTAL_SERVICE_WSDL', 'http://services.iceportal.com/Service.asmx?WSDL')
        #ICEPORTAL_SERVICE_USERNAME = getattr(settings, 'ICEPORTAL_SERVICE_USERNAME', 'distributor@simplenight.com')
        #ICEPORTAL_SERVICE_PASSWORD = getattr(settings, 'ICEPORTAL_SERVICE_PASSWORD', 'Gp*3eA')
        # url
        # http: // services.iceportal.com / Service.asmx?WSDL
        sample = {'field1': "field1" , 'field2': "field2"}
        response_url = requests.get('https://httpbin.org/get',params=sample)
        # response_url = requests.get("https://www.iceportal.com/brochures/ice/Brochure.aspx?did=20200&brochureId=ICE196&instanceid=-1&unique=06d518978bdeb808")
        # response_url = requests.get("https://www.iceportal.com/brochures/ice/Brochure.aspx", params=sample")
        if response_url != 200:
            print('bad',response_url.status_code)
            print(response_url.text)
            print(response_url.url)
            print(response_url.json)
        
        response_url.dict = response_url.json()
        print(response_url.dict)
        # for todo in response_url.json():
        # need to do a GetProperties request
        # return the data in json format
        # log the data into the suppliers table
        """
