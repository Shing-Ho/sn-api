from api import logger
from api.hotel.adapters.priceline.priceline_info import PricelineInfo
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_model import ImageType
from api.models.models import ProviderImages


class PricelineImageParser:
    def __init__(self, transport=None):
        self.adapter_info = PricelineInfo()
        self.provider = self.adapter_info.get_or_create_provider_id()

        self.transport = transport
        if self.transport is None:
            self.transport = PricelineTransport(test_mode=True)

        self.persist_count = 0

    def parse_and_save(self, limit=5):
        ProviderImages.objects.all().delete()

        initial_results = self._download_images(limit=limit)
        self._bulk_save_provider_images(initial_results["photos"])

        resume_key = initial_results["resume_key"]
        while resume_key is not None:
            try:
                results = self._download_images(resume_key=resume_key, limit=limit)
                resume_key = results["resume_key"]
                self._bulk_save_provider_images(results["photos"])
            except Exception:
                logger.exception("Error downloading images")

    def _download_images(self, limit, resume_key=None):
        response = self.transport.photos_download(resume_key=resume_key, limit=limit)
        return response["getSharedBOF2.Downloads.Hotel.Photos"]["results"]

    def _bulk_save_provider_images(self, provider_images):
        models = list(map(self._create_provider_image_model, provider_images))
        ProviderImages.objects.bulk_create(models)

        self.persist_count += len(models)
        logger.info(f"Persisted {self.persist_count} photos")

    def _create_provider_image_model(self, result):
        return ProviderImages(
            provider=self.provider,
            provider_code=result["hotelid_ppn"],
            type=ImageType.UNKNOWN,
            display_order=result["display_order"],
            image_url=result["photo_url"]
        )
