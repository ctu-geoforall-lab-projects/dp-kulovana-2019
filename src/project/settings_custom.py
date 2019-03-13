import os
from django.conf import settings

ALLOWED_HOSTS = ['gislab-vm.fsv.cvut.cz'] 

# Application definition 

INSTALLED_APPS = settings.INSTALLED_APPS + ['users.apps.UsersConfig', 'django_python3_ldap', ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(settings.BASE_DIR, 'templates')],
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

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

### CUSTOM USER MODEL ###
AUTH_USER_MODEL = 'users.CustomUser'

### LDAP AUTHENTICATION ###
AUTHENTICATION_BACKENDS = (
    'django_python3_ldap.auth.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)


LDAP_AUTH_URL = "ldap://127.0.0.1:389"

LDAP_AUTH_USE_TLS = True

LDAP_AUTH_SEARCH_BASE = "ou=people,dc=gis,dc=lab"

LDAP_AUTH_USER_FIELDS = {
    "username": "uid",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
#    "description": "description",
}

### LOGGING ###
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }
    },
    "loggers": {
        "django_python3_ldap": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
}