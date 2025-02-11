"""
Django settings for agriculture_backend_app project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta
WORKSPACE_DIR = Path.cwd()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
import dj_database_url

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w95j$xr4j!0s3v-89b5*10!p^#&^_g$ek3vh$nt1yl@f2tvv2o'
FRONTEND_AGRICULTURE_URL = os.environ.get('FRONTEND_AGRICULTURE_URL', 'http://localhost:3001')
# SECURITY WARNING: don't run with debug turned on in production!
if (os.environ.get('environment',None)=='local'):
    DEBUG = True
else:
    DEBUG = False
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "corsheaders",
    "user",
    "wallet",
    "agriculture",
    'django_otp',
    'django_otp.plugins.otp_totp',
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "notification",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_otp.middleware.OTPMiddleware'
]

ROOT_URLCONF = 'agriculture_backend_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'agriculture_backend_app.wsgi.application'
ASGI_APPLICATION = 'agriculture_backend_app.asgi.application'


if (os.environ.get('environment',None)=='prod' or os.environ.get('environment',None)=='render'):
    DATABASES = {
	"default": dj_database_url.parse(os.environ.get("AGRICULTURE_DATABASE_URL"))
    }
    CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_AGRICULTURE_URL',None))],
        },
    },
}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [('127.0.0.1', 6379)],
            },
        },
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://localhost:3000",
#     "https://127.0.0.1:3000",
#     "https://d39a-2402-a00-162-ea17-d44f-e437-a646-ced6.ngrok-free.app"
# ]
CORS_ALLOW_ALL_ORIGINS = True
APPEND_SLASH=False

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
AUTH_USER_MODEL = "user.User"
OTP_TOTP_ISSUER = "Snowvue"
OTP_TOTP_THROTTLE_FACTOR=0
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True 
EMAIL_HOST_USER = 'rajkabariya.dignizant@gmail.com' 
EMAIL_HOST_PASSWORD = 'ftif pvol pbym exxk' 
DEFAULT_FROM_EMAIL = 'rajkabariya.dignizant@gmail.com'
NOTIFICATION_EXPIRY_HOURS = os.getenv('NOTIFICATION_EXPIRY_HOURS',24)
STRIPE_API_KEY=os.getenv('STRIPE_API_KEY','sk_test_51QZRvXHPEt7mTfhh3aiAGRAa5hHUYnxaHKa4zVVFVtzkowEDt7zo85q6WSLeEBhwrRNsUe8TiBDvO8pG4kP3pb0A00t3SYkxBX')
STRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET','whsec_e5e583723cbb68db09d8341f98e210ee0021b9f90a3aad2cb7cda8560af213a1')
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "EXCEPTION_HANDLER": "agriculture_backend_app.exceptions.custom_exception_handler",
}
if (os.environ.get('environment',None)=='render'):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            # "LOCATION": "redis://127.0.0.1:6379/1",
            "LOCATION": "rediss://red-csfmo8lds78s738tomj0:jEY66zwUyVpvqaj2VI7F96KlwtJxA3MM@oregon-redis.render.com:6379",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

AGRICULTURE_DATA_UPDATE_HOURS_RANGE=os.getenv('AGRICULTURE_DATA_UPDATE_HOURS_RANGE',24)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = os.path.join(WORKSPACE_DIR, "staticfiles")
STATIC_URL = "static/"

MEDIA_ROOT = os.path.join(WORKSPACE_DIR, "media")
MEDIA_URL = "media/"
if (os.environ.get('environment',None)=='render'):
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
