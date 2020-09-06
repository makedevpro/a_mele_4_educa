from .base import *

DEBUG = False

ADMINS = (
    ('Admin', 'admin@localhost'),
)

ALLOWED_HOSTS = ['educaproject.com', 'www.educaproject.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educa',
        'USER': 'educa',
        'PASSWORD': '',
    }
}

#любой HTTP-запрос будет перенаправлен на HTTPS
SECURE_SSL_REDIRECT = True
# при работе с куками и CSRF-токенами будет учитываться SSL
CSRF_COOKIE_SECURE = True
