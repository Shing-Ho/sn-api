from api.settings import *

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL"),
        "OPTIONS": {"MAX_ENTRIES": "50000", "CLIENT_CLASS": "django_redis.client.DefaultClient"},
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "simplenight-api-db",
        "USER": "simplenight",
        "PASSWORD": "daux!bauc7nooc7YIP",
        "HOST": "35.231.161.65",
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",
            "sslrootcert": "api/secrets/server-ca.crt",
            "sslcert": "api/secrets/client-cert.pem",
            "sslkey": "api/secrets/client-key.pem",
        },
    }
}
