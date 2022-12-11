
import os
from corsheaders.defaults import default_headers

from decouple import config
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_HOSTS = []
from datetime import timedelta
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mu%1hlw9$6+5!v5cw5skvx=&=z+za^gqizc2ykm_t_#$@6(22q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
    'affluena.backends.CustomerBackend',
]

CSRF_COOKIE_NAME = "csrftoken"

# Application definition 

INSTALLED_APPS = [
    "bootstrap_admin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simple_history',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'rest_auth',
    'rest_auth.registration',
    'rest_framework',
    'rest_framework.authtoken',
    'affluena',
    'deux',
    'django_crontab',
    'axes',

 
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware'
]

ROOT_URLCONF = 'affluena.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
    
             os.path.join(BASE_DIR, 'build'),
              os.path.join(BASE_DIR, 'buildx'),
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'accounts/templates')
        ],
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
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

WSGI_APPLICATION = 'Affluena.wsgi.application'
DEUX = {
    "STEP_SIZE": 500,
    "SEND_MFA_EMAIL_FUNC": "affluena.views.send_mfa_code_email_message",
    "MFA_MODEL": "affluena.deuxModel.CustomDeux"
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


PINAX_REFERRALS_IP_ADDRESS_META_FIELD = True


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators




# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'build/static/'),os.path.join(BASE_DIR, 'buildx/static/'),os.path.join(BASE_DIR, 'templates/static'),os.path.join(BASE_DIR, 'templates')]



ACCOUNT_EMAIL_SUBJECT_PREFIX = 'Affluena - '

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
AUTH_USER_MODEL = 'Affluena.User'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_UNIQUE_USERNAME = False
ACCOUNT_USERNAME_VALIDATORS = 'home.settings.validator.custom_usename_validator'

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER':'Affluena.serializers.UserSerializer',
    'TOKEN_SERIALIZER':'Affluena.serializers.TokenSerializer',
    'LOGIN_SERIALIZER': 'Affluena.serializers.Login'
    
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER':'Affluena.serializers.SignupSerializer'
}
CORS_ALLOW_HEADERS = list(default_headers) + [
    'X-CSRFTOKEN',
]

OLD_PASSWORD_FIELD_ENABLED = True
SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD=True

ACCOUNT_ADAPTER = 'Affluena.accountadapter.CustomAccountAdapter'
CUSTOM_ACCOUNT_CONFIRM_EMAIL_URL = "/verify-email/{0}"

DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Affluena"
AXES_ENABLED = False
AXES_COOLOFF_TIME = timedelta(minutes=5)

AXES_FAILURE_LIMIT = 6
CRONTAB_COMMAND_SUFFIX = '2>&1'
CRONJOBS = [
    ('* * * * *', 'Affluena.cron.check_cron','>> ~/cron_job.log'),
    ('*/2 * * * *', 'Affluena.cron.delete_users','>> ~/delete_cron_job.log'),
    ('0 1 * * *', 'Affluena.cron.payout','>> ~/payout.log')
]

 
SESSION_COOKIE_AGE = 360
SESSION_SAVE_EVERY_REQUEST = True


