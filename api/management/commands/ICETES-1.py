#!/usr/bin/env python
import warnings
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Transport
from django.core.management.base import BaseCommand
from zeep import helpers
from api.models.models import supplier_hotels, sn_hotel_map, sn_images_map
import pandas as pd


class Command(BaseCommand):

    def handle(self, *args, **options):

        main_data = sn_hotel_map.objects.filter(provider="Ice Portal")
        transport = IcePortalTransport()
        service = transport.get_service()
        for x in range(0, len(main_data)):

            IceId = "ICE"+str(main_data[x].provider_id)
            data = service.GetVisualsV2(
                _soapheaders=transport.get_auth_header(), MappedID=IceId)
            data_as_dict = helpers.serialize_object(data)
            try:
                for item in data_as_dict['Property']['MediaGallery']['Pictures']['ImagesV2']['PropertyImageVisualsV2']:

                    sn_images_map.objects.update_or_create(
                        simplenight_id=main_data[x].simplenight_id,

                        image_type=item["Tags"],
                        image_url_path=item["mediaGalleryUrl"],
                        image_provider_id="Ice Portal"
                    )

                    print(item.keys())
                    print(item["mediaGalleryUrl"])
            except:
                pass


class IcePortalTransport:
    def __init__(self):
        self.session = self._create_wsdl_session()
        self.client = self._get_wsdl_client()

    def create_service(self, binding_name):
        target_namespace = "http://services.iceportal.com/service"
        service_binding = f"{{{target_namespace}}}{binding_name}"
        return self.client.create_service(service_binding, self._get_url())

    def get_service(self):
        return self.create_service("ICEWebServiceSoap")

    def get_auth_header(self):
        return {"ICEAuthHeaderWithMType": {"Username": self._get_username(), "Password": self._get_password()}}

    def _create_wsdl_session(self):
        session = Session()
        session.auth = HTTPBasicAuth(
            self._get_username(), self._get_password())
        return session

    def _get_wsdl_client(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning, 338)
            wsdl_path = self._get_wsdl_path()
            return Client(wsdl_path, transport=Transport(session=self.session))

    @staticmethod
    def _get_wsdl_path():
        return "http://services.iceportal.com/Service.asmx?WSDL"

    @staticmethod
    def _get_username():
        return "distributor@simplenight.com"

    @staticmethod
    def _get_password():
        return "Gp*3eA"

    @staticmethod
    def _get_url():
        return "http://services.iceportal.com/Service.asmx"


# transport = IcePortalTransport()
# service = transport.get_service()
# data = (service.GetVisualsV2(
#     _soapheaders=transport.get_auth_header(), MappedID=883))
# data_as_dict = helpers.serialize_object(data)
# for x in (data_as_dict['Property']['MediaGallery']['HD360s'].keys()):
#     print(x)
#     print(data_as_dict['Property']['MediaGallery']['HD360s'][x])
# # 20200
# transport = IcePortalTransport()
# service = transport.get_service()
# print(supplier_hotels.objects.filter(provider_name="Ice Portal").count())
# for x in supplier_hotels.objects.filter(provider_name="Ice Portal"):
#     IceId = "ICE"+str(x.provider_id)
#     print(IceId)
#     data = service.GetVisualsV2(
#         _soapheaders=transport.get_auth_header(), MappedID=IceId)
#     data_as_dict = helpers.serialize_object(data)

#     for item in data_as_dict['Property']['MediaGallery']['Pictures']['ImagesV2']['PropertyImageVisualsV2']:
#         try:
#             print(item["mediaGalleryUrl"])
#         except:
#             pass
