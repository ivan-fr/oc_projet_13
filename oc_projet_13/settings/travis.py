from . import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        "NAME": "travis_ci_test",
        "USER": "besevic",
        "PASSWORD": "unpassword",
        "HOST": "localhost",
        "PORT": "5432",
    }
}