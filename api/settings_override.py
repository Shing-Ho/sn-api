# noinspection PyUnresolvedReferences
from api.settings_test import *

# DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "db.sqlite3")}

DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "simplenight_test",
    "USER": "simplenight",
    "PASSWORD": "simplenight",
    "HOST": "localhost",
    "PORT": "5432",
}
