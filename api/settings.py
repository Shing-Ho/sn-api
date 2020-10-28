"""
Django settings for API project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import logging
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import time

import corsheaders.defaults

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "sh%sqjnk#g0_3n@(uo%&023&s6@-@-fxc277y(7+ytn)kuurq^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*", "simplenight-api-278418.ue.r.appspot.com", "127.0.0.1", "localhost"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "django_extensions",
    "api.auth",
    # Third-party
    "rest_framework",
    "rest_framework_api_key",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.common.request_cache.RequestCacheMiddleware",
    "api.common.context_middleware.RequestContextMiddleware",
]

ROOT_URLCONF = "api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            ""
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "api.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "EXCEPTION_HANDLER": "api.view.exceptions.handler",
}

DATABASES = {
    "test": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "db.sqlite3")},
    "appengine": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USERNAME"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
    },
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "d6s8eu0bcmf3s3",
        "USER": "cvgmhjuvbklqrn",
        "PASSWORD": "388c4c55c04646648e187d93a554899a69710f97cf8bfe0a3c8dc1a7909af4e5",
        "HOST": "ec2-34-233-226-84.compute-1.amazonaws.com",
        "PORT": "5432",
    },
    "local": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "simplenight",
        "USER": "simplenight",
        "PASSWORD": "simplenight",
        "HOST": "localhost",
        "PORT": "5432",
    },
    "gcloud": {
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
    },
}

active_database_label = os.environ.get("DJANGO_DATABASE", "default")
DATABASES["default"] = DATABASES[active_database_label]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

GEONAMES_CITIES_URL = "https://download.geonames.org/export/dump/cities15000.zip"
GEONAMES_CITIES_FILENAME = "cities15000.txt"
GEONAMES_ALT_NAMES_BASE_URL = "https://download.geonames.org/export/dump/alternatenames/"
GEONAMES_SUPPORTED_LANGUAGES = {"en", "es", "fr", "de", "ja", "zh", "ko", "th"}
GEONAMES_SUPPORTED_LOCATION_TYPES = {"PPL", "PPLA", "PPLA2", "PPLA3", "PPLA4", "PPLC", "PPLG"}


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "formatters": {
        "default": {
            "()": UTCFormatter,
            "format": "%(created)f %(asctime)s.%(msecs)03dZ "
            "[%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] - %(msg)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    "https://simplenightdv.github.io",
    "http://localhost",
]

CORS_ALLOW_HEADERS = list(corsheaders.defaults.default_headers) + [
    "x-api-key",
]

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
APPEND_SLASH = True

API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "OPTIONS": {"MAX_ENTRIES": "50000"},
    },
}

CACHE_TIMEOUT = 900
