# noinspection PyUnresolvedReferences
from api.settings_test import *

DATABASES["default"] = (
    {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "simplenight",
        "USER": "simplenight",
        "PASSWORD": "simplenight",
        "HOST": "localhost",
        "PORT": "5432",
    },
)
