"""
Django settings for insta_project project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import socket

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&68dn$05v^jg-@ec$euz_*spai5(-(4ngqon9a4pr)p33znw-_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'database',
    'promoting',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'insta_project.urls'

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

WSGI_APPLICATION = 'insta_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'NAME': 'insta_project',
        'USER': 'insta_project',
        'PASSWORD': 'insta_project',
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

TELEGRAM_BOT_ID = '*************************'
TELEGRAM_CHAT = None
YA_CONNECT_USER = '************'
YA_CONNECT_PASSWORD = '**********'
ONLINESIM_API = '*********************'
LUMINATI_USERNAME = '********************'
LUMINATI_PASSWORD = '*********************'
GET_PROXY_URL = '***************************'

IMAGES_DIR = os.path.join(BASE_DIR, 'images')

LOG_DIR  = os.path.join(BASE_DIR, 'logs')

HOSTNAME = socket.gethostname()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'message_only': {
            'format': '%(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)-8s %(message)s'
        },
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] [{0} %(name)s:%(lineno)s] %(message)s'.format(HOSTNAME)
        }
    },

    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'utils.file_rotate.GroupOtherWriteRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'insta_project.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'telegram_handler': {
            'level': 'DEBUG',
            'class': 'telegram_log.handler.TelegramHandler',
            'token': TELEGRAM_BOT_ID,
            'chat_ids': [TELEGRAM_CHAT],
            'err_log_name': 'console',
            'formatter': 'verbose',
        },
        'null_handler': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        '': {
            'handlers': ['telegram_handler', 'default', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['telegram_handler', 'default', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'console': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'telegram_logger': {
            'handlers': ['telegram_handler'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

if not (TELEGRAM_BOT_ID and TELEGRAM_CHAT):
    LOGGING['handlers']['telegram_handler'] = LOGGING['handlers']['null_handler']

# RabbitMQ settings
RMQ_HOST = '127.0.0.1'
RMQ_PORT = 5672
RMQ_USER = 'guest'
RMQ_PASSWORD = 'guest'

RMQ_EXCHANGE_DEFAULT = 'exchange'
RMQ_EXCHANGE_DEFAULT_TYPE = 'direct'

REDIS = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DATABASE': 0,
    }
}
