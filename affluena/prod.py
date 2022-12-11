'''Use this for production'''

from .settings import *
from decouple import config

DEBUG = False
ALLOWED_HOSTS = ['']

DATABASES = {
'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config("DB_PROD_NAME"),
        'USER': config("DB_PROD_USER"),
        'PASSWORD': config("DB_PROD_PASSWORD"),
        'HOST': config("DB_PROD_HOST"),
        'PORT': config("DB_PROD_PORT"),
    } 
} 



SITE_ID = 2
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT',cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')

