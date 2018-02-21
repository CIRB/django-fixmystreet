# Django settings for fixmystreet project.
import os


# PATH
PROJECT_PATH   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR       = PROJECT_PATH
REPORTING_ROOT = os.environ.get('REPORTING_ROOT', os.path.join(BASE_DIR, 'reporting'))
LOCALE_PATHS   = (os.path.join(PROJECT_PATH, 'locale'),)
TEMP_DIR       = os.environ.get('TEMP_DIR', '/tmp')

# ENVIRONMENT
if "ENV" in os.environ:
    ENVIRONMENT = os.environ['ENV']
else:
    ENVIRONMENT = "local"


# Manage settings according to environment
DEBUG = False

if ENVIRONMENT == "local" or ENVIRONMENT == "dev" or ENVIRONMENT == "jenkins" or ENVIRONMENT == "rpm":
    DEBUG          = True

    # Disable mail in non-production environment
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    SITE_ID = 3
    ALLOWED_HOSTS = ("*", )

elif ENVIRONMENT == "staging" or ENVIRONMENT == "testing":
    EMAIL_BACKEND = 'middleware.smtpforward.EmailBackend'
    TO_LIST       = 'django.dev@cirb.irisnet.be'
    SITE_ID       = 2
    ALLOWED_HOSTS = ("*", )

else:
    DEBUG         = False
    SITE_ID       = 1
    ALLOWED_HOSTS = ("fixmystreet-old.irisnet.be")


# VERSION
import pkg_resources
VERSION = pkg_resources.require("django-fixmystreet")[0].version


# MEDIA
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
MEDIA_URL  = '/media/'


# STATIC
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL  = '/static/'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# SOME DJANGO VAR
ADMINS                = (('Django Dev Team', 'django.dev@cirb.irisnet.be'),)
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX       = r'^/.*'
DATE_FORMAT           = "d-m-Y H:i"
DATETIME_FORMAT       = "d-m-Y H:i"
LOGIN_REQUIRED_URL    = '^/(.*)/pro/'
GA_CODE               = os.environ.get('GA_CODE', '')
ROOT_URLCONF          = 'fixmystreet_project.urls'
SECRET_KEY            = os.environ.get('SECRET_KEY', 'dev')
SESSION_SERIALIZER    = 'django.contrib.sessions.serializers.PickleSerializer'
TIME_ZONE             = 'Europe/Brussels'
DEBUGTOOLBAR_ACTIVE   = True # Can be overrided in local_settings

# Use a custom backend case insensitive for auth
#AUTHENTICATION_BACKENDS = ('middleware.backends.CaseInsensitiveModelBackend',)

# Max file upload size
MAX_UPLOAD_SIZE = "15000000"
FILE_UPLOAD_PERMISSIONS = 0644


# LANGUAGES
USE_I18N = True

LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'fr')

from django.utils.translation import ugettext_lazy as _

LANGUAGES = (
    ('fr', _('French')),
    ('nl', _('Dutch')),
    ('en', _('English')),
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'OPTIONS': {
            'debug' : DEBUG,
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'apps.fixmystreet.context_processor.domain',
                'apps.fixmystreet.context_processor.environment',
            ],
            'loaders' : [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader'
            ]
        },
    },
]


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'apps.backoffice.middleware.LoginRequiredMiddleware',
    'apps.backoffice.middleware.LoadUserMiddleware',
    'apps.fixmystreet.utils.CurrentUserMiddleware',
    'apps.fixmystreet.utils.CorsMiddleware',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.sitemaps',

    'transmeta',
    'simple_history',
    'django_extensions',
    'ckeditor',
    'monitoring',
    'stdimage',

    'rest_framework',
    'rest_framework.authtoken',

    'apps.fixmystreet.app_config.FixmystreetConfig',
    'apps.backoffice',
    'apps.fmsproxy',
    'apps.api',
    'apps.webhooks',
    'apps.fmx',
    'mobileserverstatus',
)


# LOGGING
handlers = None
if ENVIRONMENT == 'production' or ENVIRONMENT == "prod":
    handlers = ['console', 'mail_admins']
else:
    handlers = ['console', 'mail_admins', 'logstash']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'logstash': {
            'level': 'DEBUG',
            'class': 'logstash.LogstashHandler',
            'host': 'lg.irisnet.be',  #lg.irisnet.be / 195.244.165.207
            'port': 10514,  # Default value: 5959
            'filters': ['require_debug_false'],
            'version': 1,  # Version of logstash event schema. Default value: 0 (for backward compatibility of the library)
            # 'message_type': 'logstash',  # 'type' field in logstash message. Default value: 'logstash'.
            # 'fqdn': False,  # Fully qualified domain name. Default value: false.
            'tags': ['fixmystreet', 'django', ENVIRONMENT],  # list of tags. Default: None.
        },
    },
    'loggers': {
        'django': {
            'handlers': handlers,
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': handlers,
            'level': 'INFO',
            'propagate': False,
        },
        'fixmystreet': {
            'handlers': handlers,
            'level': 'INFO',
        }
    }
}


# EMAIL
if 'EMAIL_ADMIN' in os.environ:
    EMAIL_ADMIN = os.environ['EMAIL_ADMIN']
else:
    EMAIL_ADMIN = 'django.dev@cirb.irisnet.be'

ADMIN_EMAIL          = EMAIL_ADMIN
DEFAULT_FROM_EMAIL   = "Fix My Street<noreply@fixmystreet.irisnet.be>"
EMAIL_HOST           = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_SUBJECT_PREFIX = "[DJA-{0}] ".format(ENVIRONMENT[0:4])
SERVER_EMAIL         = "fixmystreet@cirb.irisnet.be"


# Load local settings
try:
    from local_settings import *
except ImportError:
    pass


# DATABASES
POSTGIS_TEMPLATE = 'template_postgis'

if not 'DATABASES' in locals() and 'DATABASE_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': os.environ['DATABASE_ENGINE'],
            'NAME': os.environ['DATABASE_NAME'],
            'USER': os.environ['DATABASE_USER'],
            'PASSWORD': os.environ['DATABASE_PASSWORD'],
            'HOST': os.environ['DATABASE_HOST'],
            'PORT': os.environ['DATABASE_PORT'],
        }
    }
elif ENVIRONMENT == "rpm":
    DATABASES = {
        'default': {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "fixmystreet.sqlite3",
        }
    }


# URBIS
PROXY_URL = "http://geoservices.irisnet.be/"
URBIS_URL = "/urbis-v2/"

if ENVIRONMENT == "local":
    URBIS_URL = PROXY_URL


# FMSPROXY
if 'FMSPROXY_URL' in os.environ:
    FMSPROXY_URL = os.environ['FMSPROXY_URL']

if 'FMSPROXY_REQUEST_SIGNATURE_KEY' in os.environ:
    FMSPROXY_REQUEST_SIGNATURE_KEY = os.environ['FMSPROXY_REQUEST_SIGNATURE_KEY']

if 'PDF_PRO_TOKEN_KEY' in os.environ:
    PDF_PRO_TOKEN_KEY = os.environ['PDF_PRO_TOKEN_KEY']


# API
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'apps.api.utils.renderers.PythonToJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'apps.api.utils.parsers.JSONToPythonParser',
    ),
    'DATETIME_FORMAT': 'iso-8601',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'apps.api.utils.renderers.PythonToJSONRenderer',
    ),
}


# CKEDITOR
CKEDITOR_UPLOAD_PATH = MEDIA_ROOT
CKEDITOR_CONFIGS = {
   'default': {
       'toolbar': [ ['Source','-','AjaxSave','Preview','-','Templates'],
                    ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Print',
                    'SpellChecker', 'Scayt'],
                    ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
                    ['Styles','Format','Font','FontSize'],
                    '/',
                    ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
                    ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
                    ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                    ['Link','Unlink','Anchor'],
                    ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar',
                    'PageBreak'],
                    ['Maximize', 'ShowBlocks','-','About']],
       'height': 300,
   },
}
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, "uploads")


# DJANGO-REGISTRATION
REGISTRATION_OPEN = False


# DEBUG TOOLBAR & JENKINS
if ENVIRONMENT != 'local' and ENVIRONMENT != 'jenkins':
    INSTALLED_APPS += ('gunicorn', )
else:
    try:
        if DEBUGTOOLBAR_ACTIVE:
            __import__('debug_toolbar')
            INSTALLED_APPS += ('debug_toolbar', )
            MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

        __import__('django_jenkins')
        INSTALLED_APPS += ('django_jenkins',)
        PROJECT_APPS = ('fixmystreet',)
        JENKINS_TASKS = (
            'django_jenkins.tasks.run_flake8',
            'django_jenkins.tasks.with_coverage',
        )
    except ImportError, e:
        print "WARNING: running `make install` in local?"
        print e


# SETTINGS SECURITY
if ENVIRONMENT != "production" and ENVIRONMENT != "prod" and EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    #disable mail in non-production environment
    raise Exception('Are you a fool ???? Do not send email as if you were in prod!!!')
