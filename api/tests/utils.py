import json
import os
from datetime import datetime, date
from typing import Callable, List


def get_test_resource_path(filename):
    return os.path.join(os.path.dirname(__file__), f"resources/{filename}")


def load_test_resource(filename):
    with open(get_test_resource_path(filename)) as f:
        return f.read()


handlers: List[Callable] = []


def register_handler(handler: Callable):
    handlers.append(handler)


# built in handlers


def datetime_handler(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    return None


def handle_default(self, obj):
    for handler in handlers:
        try:
            serialized = handler(obj)
            if serialized is not None:
                return serialized
        except TypeError:
            continue

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


register_handler(datetime_handler)

# noinspection PyTypeHints
json.JSONEncoder.default = handle_default  # type: ignore
