import abc


class AdapterInfo(abc.ABC):
    @abc.abstractmethod
    def get_name(self):
        pass

    def get_or_create_provider_id(self):
        try:
            return Provider.objects.get(name=self.get_name())
        except Provider.DoesNotExist:
            provider = Provider(name=self.get_name())
            provider.save()
            return provider
