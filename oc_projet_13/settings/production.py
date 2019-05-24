SECRET_KEY = '-~aO;| F;rE[??/w^zcumh(91'
DEBUG = False
ALLOWED_HOSTS = ['18.222.144.239']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        "NAME": "oc_projet_13",
        "USER": "ivan",
        "PASSWORD": "hWfY7Uv82k7L9f2Sr._.",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'treebeard',
    'widget_tweaks',
    'paypal.standard.ipn',
    'swingtime',
    'catalogue.apps.CatalogueConfig',
    'ventes.apps.VentesConfig',
    'session.apps.SessionConfig'
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
