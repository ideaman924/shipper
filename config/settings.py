import ast
import os

import sentry_sdk
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy
from paramiko import AuthenticationException, SSHException
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SHIPPER_SECRET_KEY")
DEBUG = int(os.environ.get("SHIPPER_DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("SHIPPER_ALLOWED_HOSTS").split(" ")

CSRF_COOKIE_SECURE = int(os.environ.get("SHIPPER_CSRF_COOKIE_SECURE", default=1))
SESSION_COOKIE_SECURE = int(os.environ.get("SHIPPER_SESSION_COOKIE_SECURE", default=1))

SECURE_HSTS_SECONDS = int(os.environ.get("SHIPPER_SECURE_HSTS_SECONDS", default=0))

with open("version.txt") as v_file:
    SHIPPER_VERSION = v_file.readline().rstrip()
    SHIPPER_SHIPPY_COMPAT_VERSION = v_file.readline().rstrip()


# Downloads Page
SHIPPER_MAIN_WEBSITE_URL = os.environ.get("SHIPPER_MAIN_WEBSITE_URL", default="#")
SHIPPER_DOWNLOADS_PAGE_MAIN_BRANDING = os.environ.get(
    "SHIPPER_DOWNLOADS_PAGE_MAIN_BRANDING", default="Downloads"
)
SHIPPER_DOWNLOADS_PAGE_DONATION_URL = os.environ.get(
    "SHIPPER_DOWNLOADS_PAGE_DONATION_URL", default="#"
)
SHIPPER_DOWNLOADS_PAGE_DONATION_MESSAGE = os.environ.get(
    "SHIPPER_DOWNLOADS_PAGE_DONATION_MESSAGE",
    default="Please consider donating, thank you!",
)


# Upload
SHIPPER_UPLOAD_VARIANTS = ast.literal_eval(
    os.environ.get(
        "SHIPPER_UPLOAD_VARIANTS",
        default='{"gapps": "GApps", "vanilla": "Vanilla (no GApps)", "foss": "FOSS", '
        '"goapps": "GoApps (Android Go Edition GApps)"}',
    )
)
SHIPPER_FILE_NAME_FORMAT = os.environ.get("SHIPPER_FILE_NAME_FORMAT")


def is_matched_name_group_in_regex(match_name, regex_pattern):
    return f"?P<{match_name}>" in regex_pattern


if not (
    is_matched_name_group_in_regex("variant", SHIPPER_FILE_NAME_FORMAT)
    and is_matched_name_group_in_regex("codename", SHIPPER_FILE_NAME_FORMAT)
    and is_matched_name_group_in_regex("date", SHIPPER_FILE_NAME_FORMAT)
    and is_matched_name_group_in_regex("version", SHIPPER_FILE_NAME_FORMAT)
):
    raise ImproperlyConfigured(
        "The regex pattern specified in SHIPPER_FILE_NAME_FORMAT is incorrect!"
    )


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "accounts",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "constance.backends.database",
    "rest_framework",
    "rest_framework.authtoken",
    "shipper",
    "downloads",
    "api",
    "drf_chunked_upload",
    "auditlog",
    "django_celery_beat",
    "django_celery_results",
    "django_cleanup.apps.CleanupConfig",  # must be last for successful deletions
]

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.download_page_processor",
                "config.context_processors.version_processor",
                "config.context_processors.debug_mode_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "SHIPPER_SQL_ENGINE", default="django.db.backends.sqlite3"
        ),
        "NAME": os.environ.get(
            "SHIPPER_SQL_DATABASE", default=os.path.join(BASE_DIR, "db.sqlite3")
        ),
        "USER": os.environ.get("SHIPPER_SQL_USER", default="user"),
        "PASSWORD": os.environ.get("SHIPPER_SQL_PASSWORD", default="password"),
        "HOST": os.environ.get("SHIPPER_SQL_HOST", default="localhost"),
        "PORT": os.environ.get("SHIPPER_SQL_PORT", default="5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{name}"}
    for name in [
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    ]
]


# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "shipper-cache",
    }
}
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = "shipper"


# Email
EMAIL_BACKEND = os.environ.get(
    "SHIPPER_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("SHIPPER_EMAIL_HOST", default="")
EMAIL_PORT = os.environ.get("SHIPPER_EMAIL_PORT", default="")
EMAIL_HOST_USER = os.environ.get("SHIPPER_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = os.environ.get("SHIPPER_EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = int(os.environ.get("SHIPPER_EMAIL_USE_TLS", default=1))
DEFAULT_FROM_EMAIL = os.environ.get("SHIPPER_DEFAULT_FROM_EMAIL", default="")

ADMINS = [
    tuple(i.split(":"))
    for i in os.environ.get("SHIPPER_ADMIN_EMAILS", default="").split(";")
]
MANAGERS = ADMINS

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("ko", gettext_lazy("Korean")),
    ("en", gettext_lazy("English")),
]

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Media
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Login
LOGIN_REDIRECT_URL = "/maintainers/"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "10/minute", "user": "10/second"},
}


# drf-chunked-upload
DRF_CHUNKED_UPLOAD_COMPLETE_EXT = ""
DRF_CHUNKED_UPLOAD_ABSTRACT_MODEL = False
DRF_CHUNKED_UPLOAD_CHECKSUM = os.environ.get("SHIPPER_UPLOAD_CHECKSUM", default="sha256")
DRF_CHUNKED_UPLOAD_MAX_BYTES = 5_000_000_000  # 5 GB


# Celery
CELERY_BROKER_URL = "pyamqp://rabbitmq:5672/"
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_CACHE = "django-cache"


# Constance
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_CONFIG = {
    "SHIPPER_MAIN_WEBSITE_URL": ("#", "Link to redirect users to when they click on the 'Back to main website' button on the top of the page. Setting this configuration to the pound symbol disables redirection and hides the button.", str),
    "SHIPPER_DOWNLOADS_PAGE_MAIN_BRANDING": ("Downloads", "Sets the navbar branding at the top left of the website.", str),
    "SHIPPER_DOWNLOADS_PAGE_DONATION_URL": ("#", "URL to refer users to when they wish to donate.", str),
    "SHIPPER_DOWNLOADS_PAGE_DONATION_MESSAGE": ("Please consider donating, thank you!", "Donation message to show to users in the donation banner.", str),
    "SHIPPER_UPLOAD_VARIANTS": ('{"gapps": "GApps","vanilla": "Vanilla (no GApps)","foss": "FOSS","goapps": "GoApps (Android Go Edition GApps)"}', "Allowed upload variant pairing in JSON format.", str),
    "SHIPPER_FILE_NAME_FORMAT": ("[A-Za-z]*-(?P<version>[a-z0-9.]*)-(?P<codename>[A-Za-z]*)-OFFICIAL-(?P<variant>[a-z]*)-(?P<date>[0-9]*).zip", "Regex pattern to use when parsing file names of uploaded artifacts. The pattern must include the following four named match groups; otherwise an exception will occur during uploading: `version', `codename`, `variant`, and `date`.", str),
    "SHIPPER_UPLOAD_CHECKSUM": ("sha256", "Checksum type shipper expects when uploading via the chunked upload API. Supports `sha256` and `md5`.", str),
}


# Sentry SDK
def before_send(event, hint):
    if "log_record" in hint:
        if hint["log_record"].name == "django.security.DisallowedHost":
            return None
    return event


if DEBUG == 1:
    sentry_transaction_rate = 1.0
else:
    sentry_transaction_rate = 0.2


sentry_sdk.init(
    dsn=os.environ.get("SHIPPER_SENTRY_SDK_DSN", default=""),
    integrations=[DjangoIntegration()],
    release=f"{SHIPPER_VERSION}",
    traces_sample_rate=sentry_transaction_rate,
    send_default_pii=os.environ.get("SHIPPER_SENTRY_SDK_PII", default=False),
    before_send=before_send,
    ignore_errors=[SSHException, AuthenticationException, ConnectionRefusedError],
)
