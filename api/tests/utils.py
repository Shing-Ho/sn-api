import json
import os
import string
import random

from api.auth.models import Organization, OrganizationAPIKey


def get_test_resource_path(filename):
    return os.path.join(os.path.dirname(__file__), f"resources/{filename}")


def load_test_resource(filename):
    with open(get_test_resource_path(filename)) as f:
        return f.read()


def load_test_json_resource(filename):
    with open(get_test_resource_path(filename)) as f:
        return json.load(f)


def random_alphanumeric(length=8):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def create_api_key(organization_name="anonymous"):
    try:
        organization = Organization.objects.get(name=organization_name)
    except Organization.DoesNotExist:
        organization = Organization.objects.create(name=organization_name, api_daily_limit=100, api_burst_limit=5)

    api_key, key = OrganizationAPIKey.objects.create_key(name="test-key", organization=organization)

    return key
