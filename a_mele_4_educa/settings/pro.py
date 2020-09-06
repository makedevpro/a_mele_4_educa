from .base import *

DEBUG = False

ADMINS = (
    ('Admin', 'admin@localhost'),
)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educa',
        'USER': 'educa',
        'PASSWORD': '',
    }
}
