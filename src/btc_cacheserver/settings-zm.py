#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django settings for btc_cacheserver project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import django

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v$v15$r(&he1m+tl8-ogj%t&osbg8hv)0$^%%-nq=-b+x$3oco'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
APPEND_SLASH=False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'btc_cacheserver.contract',
    'btc_cacheserver.blockchain',
    'channels',
    'corsheaders'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'btc_cacheserver.urls'

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

# WSGI_APPLICATION = 'btc_cacheserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'NAME'    : 'blockchain',
        'USER'    : 'root',
        'PASSWORD': 'h7wFdCZN2NubZonbXAs1mYUf',
        'HOST'    : '10.2.0.5',
        'PORT'    : 3306,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ("*")
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'procedure': {
            'format': '[%(asctime)s] [%(threadName)s:%(thread)d] [%(name)s] %(message)s', 
        }, #日志格式
        'django':{
            'format': '[%(asctime)s] [%(threadName)s:%(thread)d] [%(name)s] [%(pathname)s:%(lineno)s] [%(funcName)s] [%(levelname)s]-%(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {

    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django'
        },
        'procedure': {
            'level':'DEBUG',
            'class': 'logging.StreamHandler',
            # 'class':'cloghandler.ConcurrentRotatingFileHandler',
            # 'filename':'/home/zhangmin/workdir/btc_cacheserver/src/consumer.log',
            # 'maxBytes': 1024*1024*50,
            # 'backupCount': 20,
            'formatter':'procedure',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'scripts': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False
        },
        'procedure': {
            'handlers': ['procedure',  ],
            'level': 'INFO',
            'propagate': False
        },
    }
}
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "asgiref.inmemory.ChannelLayer",
#         "ROUTING": "btc_cacheserver.blockchain.routing.channel_routing",
#     },
# }

REDIS = {
    "HOST" : "10.2.0.1",
    "PORT" : 6379,
    "AUTH" : "h7wFdCZN2NubZonbXAs1mYUf",
    "DB"   : 15,
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', "redis://:{}@{}:{}/15".format(REDIS["AUTH"], REDIS["HOST"], REDIS["PORT"]))],
        },
        "ROUTING": "btc_cacheserver.blockchain.routing.channel_routing",
    },
}
# MQ_CONFIG
MQ_HOST     = "10.2.0.150"
MQ_PORT     = 5672
MQ_USER     = "admin"
MQ_PASSWORD = "admin"

WRITE_BLOCKCHAIN_QUEUE    = "write_blockchain_queue"
WRITE_BLOCKCHAIN_EXCHANGE = "write_blockchain_exchange"
CHECK_BLOCKCHAIN_QUEUE    = "check_blockchain_queue"
CHECK_BLOCKCHAIN_QUERY    = "check_blockchain_query"
CHECK_BLOCKCHAIN_EXCHANGE = "check_blockchain_exchange"
REWRITE_BLOCKCHAIN_QUEUE    = "write_blockchain_queue_re"

BLOCKCHAIN_ACCOUNT        = "0x3b2BD2ad09FC693119736b6E038Cd2343B9F8D2a"
BLOCKCHAIN_PASSWORD       = "123456"
BLOCKCHAIN_RPC_HOST       = "10.0.0.28"
BLOCKCHAIN_RPC_PORT       = "8020"
BLOCKCHAIN_RPC_HOST_0     = "10.0.0.28"
BLOCKCHAIN_RPC_PORT_0     = "8020"
BLOCKCHAIN_RPC_HOST_1     = "10.0.0.29"
BLOCKCHAIN_RPC_PORT_1     = "8020"
BLOCKCHAIN_CALL_GAS_LIMIT = 4500000
TRANSACTION_MAX_WAIT      = 600

# CONTROLLER_ROUTE_ADDRESS = "0xc13aEc0e45032c191e0C055BBF4ad67e066237A3"
# CONTROLLER_ROUTE_ADDRESS = "0x2270B8e204eAc6B9013bb62093B105d719be8a35"
CONTROLLER_ROUTE_ADDRESS = "0x6D524dDc3b555FA921b4A716c30013B37b126774"
# CONTROLLER_ROUTE_ADDRESS = "0xD06260ed5bA63a8805e55E7a1442Ba661399438d"

# USER_LOAN_STORE_ROUTE_ADDRESS = "0x63C48C36d69d7b580784de56C77718A778990B3d"
# USER_LOAN_STORE_ROUTE_ADDRESS = "0x1D0CAD1044e92AadA0d3f1fF10eaE2CC6a544c48"
USER_LOAN_STORE_ROUTE_ADDRESS = "0x4f4D986596771425eE6bC224785E474FC1824fB2"

LOAN_CONTRACT_ROUTE_ADDRESS = "0xafeC10f780f09c0FB071FCdF5B91B1D9F0AE1E54"

# INTERFACE_ADDRESS        = "0x40c3bA573fE3D01EfD010B7989EEe354a3240151"
# INTERFACE_ADDRESS        = "0x91CD23399851376F6a8d3938D7f55a3e79003C69"
# INTERFACE_ADDRESS        = "0xa35E196B77158B6627e4803A3C50223a7584d00C"
INTERFACE_ADDRESS        = "0xcB85ad01F2662c09E1C185C9FD78C34F96F49BE9"


CONTRACT_DIR = os.path.join(BASE_DIR, "sol")

TOKEN_ADDRESS = "0x1AE7434fB8A74C64f1a80c1Ab4221004A9C25Aad"
INTERFACE_ABI_FILE = BASE_DIR + "/sol/Interface-abi.json"
INTERFACE_SOL_FILE = BASE_DIR + "/sol/Interface.sol"
USERLOAN_FILE = BASE_DIR + '/sol/UserLoan.json'
django.setup()
