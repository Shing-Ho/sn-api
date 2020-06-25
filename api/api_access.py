import dataclasses
from typing import ClassVar, Type

import marshmallow_dataclass
from rest_framework_api_key.models import APIKey
from marshmallow import Schema
from api import logger


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class ApiAccessRequest:
    name: str
    Schema: ClassVar[Type[Schema]] = Schema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class ApiAccessResponse:
    api_key: str
    key: str
    Schema: ClassVar[Type[Schema]] = Schema


def create_anonymous_api_user(request: ApiAccessRequest):
    logger.info(f"Creating API Key for user {request.name}")
    api_key, key = APIKey.objects.create_key(name=request.name)

    return ApiAccessResponse(api_key=api_key, key=key)



