#!/usr/bin/env python
import warnings

from django.core.management.base import BaseCommand
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Transport

from api import logger
from api.hotel.hotel_api_model import ImageType
from api.models.models import ProviderImages, Provider


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.transport = IcePortalTransport()
        self.provider = Provider.objects.get_or_create(name="iceportal")[0]

    def handle(self, *args, **options):
        properties = self.transport.get_service().GetProperties(_soapheaders=self.transport.get_auth_header())

        for iceportal_property in properties["info"]["PropertyIDInfo"]:
            mapped_id = iceportal_property["mappedID"]
            logger.info("Parsing images for IcePortal ID: " + mapped_id)
            try:
                self._parse_and_save_images(mapped_id)
            except Exception:
                logger.exception("Error while loading hotel")

    def _parse_and_save_images(self, iceportal_id):
        visuals = self.transport.get_service().GetVisualsV2(
            _soapheaders=self.transport.get_auth_header(), MappedID=iceportal_id
        )

        iceportal_id = visuals["Property"]["PropertyInfo"]["iceID"]
        images = visuals["Property"]["MediaGallery"]["Pictures"]["ImagesV2"]["PropertyImageVisualsV2"]

        provider_image_models = []
        for image in images:
            display_order = image["ordinal"]
            fullsize_url = image["DirectLinks"]["Url"]
            provider_image_models.append(
                ProviderImages(
                    provider=self.provider,
                    provider_code=iceportal_id,
                    display_order=display_order,
                    type=ImageType.UNKNOWN.value,
                    image_url=fullsize_url,
                )
            )

        ProviderImages.objects.bulk_create(provider_image_models)


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
        session.auth = HTTPBasicAuth(self._get_username(), self._get_password())
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
