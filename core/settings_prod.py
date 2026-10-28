# core/settings_prod.py
"""Configuración de producción — Render.com (versión final W03).

Hereda settings.py y sobreescribe lo necesario para producción.

Variables de entorno requeridas en Render:
    SECRET_KEY              -> clave aleatoria
    DATABASE_URL            -> la entrega Render PostgreSQL
    DJANGO_SETTINGS_MODULE  -> core.settings_prod
    ALLOWED_HOSTS           -> opcional (Render inyecta RENDER_EXTERNAL_HOSTNAME)
"""
from .settings import *   # hereda toda la configuración base
import os
import dj_database_url

# ── SEGURIDAD BÁSICA ───────────────────────────────────────────────
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']   # falla a propósito si no existe

# ── HOSTS PERMITIDOS ───────────────────────────────────────────────
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
_extra_hosts = os.environ.get('ALLOWED_HOSTS', '').split(',')

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + (
    [_render_host] if _render_host else []
) + [h for h in _extra_hosts if h]

# ── BASE DE DATOS: PostgreSQL via DATABASE_URL ─────────────────────
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# ── CSRF: dominios de confianza ────────────────────────────────────
CSRF_TRUSTED_ORIGINS = []
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

# ── HEADERS HTTP SEGUROS ───────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

# ── ARCHIVOS ESTÁTICOS (WhiteNoise) ────────────────────────────────
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── LOGGING: solo WARNING y superiores ─────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django.security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ── ALMACENAMIENTO DE ARCHIVOS MEDIA (producción) — W11 ───────────────────
# Solo se activa si en Render existe la variable AWS_STORAGE_BUCKET_NAME.
# Variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
#            AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME
_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

if _bucket:
    DEFAULT_FILE_STORAGE    = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID       = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY   = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = _bucket
    AWS_S3_REGION_NAME      = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_DEFAULT_ACL         = None    # el bucket controla el acceso
    AWS_S3_FILE_OVERWRITE   = False   # no sobreescribir archivos con el mismo nombre
    AWS_QUERYSTRING_AUTH    = False   # URLs públicas (sin firma)
    MEDIA_URL               = f'https://{_bucket}.s3.amazonaws.com/'
