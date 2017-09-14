import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = False
# TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'authtools',
    'django_extensions',

    'bootstrap3',

    # 'social.apps.django_app.default',
    'social_django',

    'users',

    'website',
    'projects',
    'q13es',
    'student_applications',
    'surveys',
    'events',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'oglam.urls'

WSGI_APPLICATION = 'oglam.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'oglam',
        # 'USER': 'oglam',
        # 'PASSWORD': 'oglam',
        # 'HOST': 'localhost',
    }
}

LANGUAGE_CODE = 'he-il'
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'oglam', 'locale'),
)

TIME_ZONE = 'Asia/Jerusalem'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Users
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "sa:dashboard"
LOGIN_ERROR_URL = "users:login"
VALIDATE_LINK_DAYS = 7

SOCIAL_AUTH_RAISE_EXCEPTIONS = False
# SOCIAL_AUTH_EMAIL_FORM_URL = "users:signup"
SOCIAL_AUTH_EMAIL_FORM_HTML = "users/signup.html"
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'oglam.socialauth.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = 'users:validation_sent'

EMAIL_FROM = "OpenGLAM <noreply@oglam.hasadna.org.il>"

# SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# SOCIAL_AUTH_PIPELINE = (
#     # Get the information we can about the user and return it in a simple
#     # format to create the user instance later. On some cases the details are
#     # already part of the auth response from the provider, but sometimes this
#     # could hit a provider API.
#     'social.pipeline.social_auth.social_details',
#
#     # Get the social uid from whichever service we're authing thru. The uid is
#     # the unique identifier of the given user in the provider.
#     'social.pipeline.social_auth.social_uid',
#
#     # Verifies that the current auth process is valid within the current
#     # project, this is were emails and domains whitelists are applied (if
#     # defined).
#     'social.pipeline.social_auth.auth_allowed',
#
#     # Checks if the current social-account is already associated in the site.
#     'social.pipeline.social_auth.social_user',
#
#     # Make up a username for this person, appends a random string at the end if
#     # there's any collision.
#     'social.pipeline.user.get_username',
#
#     # Send a validation email to the user to verify its email address.
#     # 'social.pipeline.mail.mail_validation',
#
#     # Associates the current social details with another user account with
#     # a similar email address.
#     # 'social.pipeline.social_auth.associate_by_email',
#
#     # Create a user account if we haven't found one yet.
#     # 'social.pipeline.user.create_user',
#     'oglam.socialauth.create_user',
#
#     # Create the record that associated the social account with this user.
#     'social.pipeline.social_auth.associate_user',
#
#     # Populate the extra_data field in the social record with the values
#     # specified by settings (and the default ones like access_token, etc).
#     'social.pipeline.social_auth.load_extra_data',
#
#     # Update the user record with any changed info from the auth service.
#     'social.pipeline.user.user_details'
# )
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'users.socialauth.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'users.socialauth.notify_managers',
)
SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
]

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
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
                'utils.context_processors.hackita_processor',
            ],
        },
    },
]

# TEMPLATE_CONTEXT_PROCESSORS = (
#     'django.template.context_processors.i18n',
#     'django.template.context_processors.media',
#     'django.template.context_processors.static',
#     'django.template.context_processors.tz',
#     'django.contrib.messages.context_processors.messages',
# )


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'collected-static')
STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },

    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }
}

# Default settings
BOOTSTRAP3 = {
    'required_css_class': 'required',
}

import utils.mail
utils.mail.fix_django_mail_encoding()

