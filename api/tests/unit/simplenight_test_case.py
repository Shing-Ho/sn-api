from unittest.mock import Mock

from django.test import TestCase

from api.common.context_middleware import RequestContextMiddleware
from api.common.request_cache import RequestCacheMiddleware


class SimplenightTestCase(TestCase):
    def setUp(self) -> None:
        self.request_cache = RequestCacheMiddleware(Mock())
        self.request_context = RequestContextMiddleware()
        self.request_cache.process_request(Mock())
