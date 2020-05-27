import os


def get_test_resource_path(filename):
    return os.path.join(os.path.dirname(__file__), f"resources/{filename}")


def load_test_resource(filename):
    with open(get_test_resource_path(filename)) as f:
        return f.read()