import abc
from typing import Dict, Any

import requests

from api import logger
from api.common.models import BaseSchema, to_json, to_jsons


class Transport(abc.ABC):
    def __init__(self):
        self._headers = {
            "Accept-Encoding": "gzip",
        }

    @abc.abstractmethod
    def _get_headers(self, **kwargs):
        pass

    def _get_default_headers(self):
        return self._headers.copy()

    def post(self, url, request: BaseSchema, **kwargs):
        response = requests.post(url, json=to_json(request), headers=self._get_headers(**kwargs))
        self._log_request(url, request, response)

        return response

    def post_params(self, url, params: Dict[Any, Any], **kwargs):
        response = requests.post(url, json=params, headers=self._get_headers(**kwargs))
        self._log_request(url, params, response)

        return response

    def get(self, url, params: Dict, **kwargs):
        params.update(kwargs)

        response = requests.get(url, params=params, headers=self._get_headers())
        self._log_request(url, params, response)

        return response

    @staticmethod
    def _log_request(url, request, response):
        if hasattr(request, "Schema"):
            request = to_jsons(request)

        logger.debug(
            {
                "url": url,
                "request": request,
                "status": response.ok,
                "status_code": response.status_code,
                "response": response.text,
            }
        )
