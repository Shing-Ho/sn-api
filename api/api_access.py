import dataclasses
from typing import ClassVar, Type

import marshmallow_dataclass
from marshmallow import Schema

from api import logger
from api.auth.models import OrganizationAPIKey, Organization


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

    anonymous_org = Organization.objects.get(name="anonymous")
    api_key, key = OrganizationAPIKey.objects.create_key(name=request.name, organization=anonymous_org)

    return ApiAccessResponse(api_key=api_key, key=key)



