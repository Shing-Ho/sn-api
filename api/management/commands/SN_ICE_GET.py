# -*- coding: utf-8 -*-
#!/usr/bin/env python

import requests
import datetime
import pandas as pd
from api.models.models import sn_images_map
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from zeep import xsd

session = Session()
auth = HTTPBasicAuth('distributor@simplenight.com', 'Gp*3eA')
client = Client('http://services.iceportal.com/Service.asmx?WSDL',
                transport=Transport(session=session))


# get list of all properties from our - do in df
#df = pd.DataFrame(list(sn_images_map.object.all().values()))
df = pd.DataFrame(list(sn_images_map.object.all().values('simplenight_city_id', 'thumbnail_image')))
df = df.to_json()
print(df)
# queryset = sn_images_map.objects.all()

# Main image for a particular property plus thumbnail

#  pass in the ice id from the property to get that main image
'''
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
'''