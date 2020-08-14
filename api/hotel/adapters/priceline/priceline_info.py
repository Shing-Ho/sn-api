from api.models.models import Provider


class PricelineInfo:
    name = "priceline"

    @staticmethod
    def get_or_create_provider_id():
        try:
            provider = Provider.objects.get(name=PricelineInfo.name)
            return provider
        except Provider.DoesNotExist:
            provider = Provider(name=PricelineInfo.name)
            provider.save()
            return provider
