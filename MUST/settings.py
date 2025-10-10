from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# Security and Debug Settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'False'

# Allowed Hosts Configuration
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '63.180.6.177',
    'ec2-63-180-6-177.eu-central-1.compute.amazonaws.com',
    '.app.github.dev',  # This allows all VS Code forwarded URLs
]

# Ensure SECRET_KEY is not empty
if not SECRET_KEY:
    raise ValueError("The DJANGO_SECRET_KEY environment variable must be set")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'tinymce',
    'account.apps.AccountConfig',
    'blog',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'corsheaders',
    'comments',
    'feedback',
    'testimonials',
    'partners',
    'Club',
    'drf_yasg',
    'events',
    'communities',
    'communications',
]

SITE_ID = 2

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]


ROOT_URLCONF = 'MUST.urls'
WSGI_APPLICATION = 'MUST.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', 0)),
        'CONN_HEALTH_CHECKS': os.getenv('DB_CONN_HEALTH_CHECKS', 'False') == 'True',
        'OPTIONS': {
            'init_command': os.getenv('DB_INIT_COMMAND'),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
            'use_unicode': os.getenv('DB_USE_UNICODE', 'True') == 'True',
            'autocommit': os.getenv('DB_AUTOCOMMIT', 'True') == 'True',
            'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', 10)),
            'read_timeout': int(os.getenv('DB_READ_TIMEOUT', 30)),
            'write_timeout': int(os.getenv('DB_WRITE_TIMEOUT', 30)),
            'sql_mode': os.getenv('DB_SQL_MODE', 'TRADITIONAL'),
            'isolation_level': os.getenv('DB_ISOLATION_LEVEL', 'read committed'),
        },
        'ATOMIC_REQUESTS': os.getenv('DB_ATOMIC_REQUESTS', 'True') == 'True',
    }
}





# Authentication and Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend"
]

# Social Authentication Providers
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "scope": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"}
    },
    "github": {
        "APP": {
            "client_id": os.environ.get('GITHUB_CLIENT_ID'),
            "secret": os.environ.get('GITHUB_CLIENT_SECRET'),
        }
    }
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_SIGNATURE_VERSION = os.environ.get('AWS_S3_SIGNATURE_VERSION', 's3v4')
AWS_S3_FILE_OVERWRITE = os.environ.get('AWS_S3_FILE_OVERWRITE', 'False').lower() == 'true'

# Templates Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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


CORS_ALLOWED_ORIGINS = [
    'https://meru-innovators-club-frontend.vercel.app',
    'http://localhost:4200',
]

CORS_ALLOW_CREDENTIALS = True

# CSRF Setting
CSRF_TRUSTED_ORIGINS = [
    'https://meru-innovators-club-frontend.vercel.app',
    'http://localhost:4200',
    'https://n87qqn9j-3000.euw.devtunnels.ms/'
]

# JWT and Authentication Settings
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "KEY_PREFIX": "events_api",
        "TIMEOUT": 300,
    }
}

FRONTEND_BASE_URL = 'https://meru-innovators-club-frontend.vercel.app'

APPEND_SLASH = True