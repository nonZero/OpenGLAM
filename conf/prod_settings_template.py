_user = '{{webuser}}'
_host = '{{host}}'

ALLOWED_HOSTS = [
    _host,
    'register.oglam.hasadna.org.il',
]

DEFAULT_FROM_EMAIL = "Open GLAM <noreply@%s>" % _host
EMAIL_SUBJECT_PREFIX = '[%s] ' % _user.upper()

ADMINS = (
    ('Udi', 'udioron@gmail.com'),
)

MANAGERS = ADMINS

SECRET_KEY = '{{secret_key}}'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': _user,
        'USER': _user,
        'PASSWORD': _user,
        'HOST': 'localhost',
        'PORT': '',
    },
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

GOOGLE_ANALYTICS_ID = ''

SECURE_PROXY_SSL_HEADER = ('HTTP_X_SCHEME', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
