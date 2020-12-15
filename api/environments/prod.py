from api.settings import *  # noqa F403
import os
import bugsnag

bugsnag.configure(release_stage="PROD")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL"),
        "OPTIONS": {"MAX_ENTRIES": "50000", "CLIENT_CLASS": "django_redis.client.DefaultClient"},
    },
}

BUGSNAG = {
    "api_key": os.environ.get("BUGSNAG_API_KEY"),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USERNAME"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",
            "sslrootcert": "api/secrets/prod/server-ca.crt",
            "sslcert": "api/secrets/prod/client-cert.pem",
            "sslkey": "api/secrets/prod/client-key.pem",
        },
    }
}
