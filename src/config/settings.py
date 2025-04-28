from datetime import datetime
import os
from pathlib import Path



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^u^6oq!6n!8hp*w2i09scvbq+48vnm)y$psfzxe7e-%k-zf66&"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",  # Required for DRF
    "django.contrib.sessions",      # Required for middleware
    "django.contrib.staticfiles",
    'rest_framework',
    "url_shortener",
    'django_redis',  # For caching
    'celery',  # For background tasks
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Rate limiting configuration (using DRF throttling)
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/min',  # 5 requests per minute
    }
}

ROOT_URLCONF = "src.config.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "src.config.wsgi.application"





DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bee_orders', 
        'USER': 'admin',      
        'PASSWORD': 'QydMKBLYb3nHqVkX8TFP5jCrpEuStA9N',  
        'HOST': '77.37.120.167',         
        'PORT': '5431',             
        'TEST': {
            'NAME': 'test_bee_orders', 
        },
    }
}

# Celery configuration
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

# Caching setup
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Directory where logs are stored
LOGS_DIR = Path(BASE_DIR) / 'logs'

# Ensure the log directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
    
# Define product catalog service base URL
PRODUCT_CATALOG_BASE_URL = "https://staging.bookbee.info/beeback/prod/api/stock"


# Generate timestamp for log file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
pid = os.getpid()  # Get the current process ID

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'skip_autoreload': {
             '()': 'src.utils.logging_filters.SkipAutoreloadFilter',

        },
    },
    'formatters': {
        'verbose': {
            'format': '[{levelname}] [{asctime}] [{module}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['skip_autoreload'],  # Apply filter to console
            'formatter': 'verbose',
        },
        'rotating_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, f'application_{timestamp}.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 3,
            'filters': ['skip_autoreload'],  # Apply filter to file logs
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'filters': ['skip_autoreload'],  # Apply filter to error logs
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'rotating_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}