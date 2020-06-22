import json
import os
import string
import random


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
