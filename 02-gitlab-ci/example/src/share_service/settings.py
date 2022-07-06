import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "u_1=qdfe*rzrvj9e4#&9y)8!uuwg+m81-+-at02q62d9fykso=")

DEBUG = int(os.environ.get("DEBUG", default=1))

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(" ")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")

CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA", "undefined")

CI_COMMIT_REF_NAME = os.environ.get("CI_COMMIT_REF_NAME", "undefined")

INSTALLED_APPS = [
    "jet",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_yasg",
    "oauth2_provider",
    "social_django",
    "rest_framework_social_oauth2",
    "django_celery_beat",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "crum.CurrentRequestUserMiddleware",
]

ROOT_URLCONF = "share_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "share_service.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "share_service"),
        "USER": os.environ.get("DB_USER", "share_service"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "share_service"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/staticfiles/"
MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://0.0.0.0:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER", "redis://0.0.0.0:6379/0")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

AUTH_USER_MODEL = "core.User"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", "")

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

DRFSO2_URL_NAMESPACE = "api"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework_social_oauth2.authentication.SocialAuthentication",
    ),
}

AUTHENTICATION_BACKENDS = (
    "rest_framework_social_oauth2.backends.DjangoOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

X_FRAME_OPTIONS = "SAMEORIGIN"

JET_THEMES = [
    {"theme": "default", "color": "#47bac1", "title": "Default"},
    {"theme": "green", "color": "#44b78b", "title": "Green"},
    {"theme": "light-green", "color": "#2faa60", "title": "Light Green"},
    {"theme": "light-violet", "color": "#a464c4", "title": "Light Violet"},
    {"theme": "light-blue", "color": "#5EADDE", "title": "Light Blue"},
    {"theme": "light-gray", "color": "#222", "title": "Light Gray"},
]

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "site@mircod.com"
EMAIL_HOST_SENDER = "Share Service"
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = 587

if ENVIRONMENT == "local":
    INSTALLED_APPS.append("rosetta")
    ROSETTA_SHOW_AT_ADMIN_PANEL = True

LANGUAGES = [("ru", _("Русский")), ("en", _("Английский"))]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "core/locale"),
]

VERIFICATION_TOKEN_EXPIRATION_TIME: int = 60 * 60  # 1 hour

SENTRY_DSN = os.environ.get("SENTRY_DSN")
ENABLE_SENTRY = False

if SENTRY_DSN and CI_COMMIT_SHA:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.logging import ignore_logger

    ignore_logger("django.security.DisallowedHost")

    ENABLE_SENTRY = True

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        release=CI_COMMIT_SHA,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        environment=ENVIRONMENT,
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

CODESANDBOX_URL = "https://sedl3.csb.app"
CORS_ORIGIN_WHITELIST = ["http://localhost:3000", CODESANDBOX_URL]
CORS_ALLOWED_ORIGINS = CORS_ORIGIN_WHITELIST
