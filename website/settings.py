"""
Django settings for website project.
"""
import os
from pathlib import Path
import environ
from oscar.defaults import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializar django-environ
env = environ.Env(
    # Valores por defecto con type casting
    DEBUG=(bool, True),
)

# Leer archivo .env
environ.Env.read_env(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de flatpages
    'django.contrib.sites',
    'django.contrib.flatpages',
    # Aplicaciones de oscar
    'oscar.config.Shop',
    'oscar.apps.analytics.apps.AnalyticsConfig',
    'apps.address.apps.AddressConfig',  # Fork personalizado
    'apps.shipping.apps.ShippingConfig',  # Fork personalizado
    'apps.basket.apps.BasketConfig', 
    'apps.checkout.apps.CheckoutConfig',
    'apps.catalogue.apps.CatalogueConfig',
    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
    'oscar.apps.communication.apps.CommunicationConfig',
    'oscar.apps.partner.apps.PartnerConfig',
    'oscar.apps.payment.apps.PaymentConfig',
    'oscar.apps.offer.apps.OfferConfig',
    'oscar.apps.order.apps.OrderConfig',
    'oscar.apps.customer.apps.CustomerConfig',
    'oscar.apps.search.apps.SearchConfig',
    'oscar.apps.voucher.apps.VoucherConfig',
    'oscar.apps.wishlists.apps.WishlistsConfig',
    'oscar.apps.dashboard.apps.DashboardConfig',
    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
    'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
    'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',

    # 3rd-party apps that oscar depends on
    'widget_tweaks',
    'haystack',
    'treebeard',
    'sorl.thumbnail',   # Default thumbnail backend, can be replaced
    'django_tables2',

    # Tailwind CSS integration
    "tailwind",
    'theme',
]

if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware de flatpages
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Middleware de Oscar (Añadir este)
    'oscar.apps.basket.middleware.BasketMiddleware',
]

if DEBUG:
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Procesadores requeridos por Oscar
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.communication.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
                
                # Context processor personalizado de XYZ Studio
                'website.context_processors.shop_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Soporta tanto DATABASE_URL como variables individuales para Docker

if env('DATABASE_URL', default=None):
    # Usar DATABASE_URL si está definida (formato: postgres://user:pass@host:port/dbname)
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
elif env('DATABASE_HOST', default=None):
    # Usar variables individuales (típico en Docker)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DATABASE_NAME', default='xyz_studio'),
            'USER': env('DATABASE_USER', default='xyz_user'),
            'PASSWORD': env('DATABASE_PASSWORD', default=''),
            'HOST': env('DATABASE_HOST', default='localhost'),
            'PORT': env('DATABASE_PORT', default='5432'),
            'CONN_MAX_AGE': env.int('DATABASE_CONN_MAX_AGE', default=60),
        }
    }
else:
    # Fallback a SQLite para desarrollo local sin Docker
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Lima'


USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'theme/static')]

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Configuración básica de Oscar
OSCAR_SHOP_NAME = 'XYZ Studio'
OSCAR_SHOP_TAGLINE = 'Decoración e Impresión 3D'
OSCAR_DEFAULT_CURRENCY = 'PEN'  # Sol Peruano

# Repositorio de envíos personalizado
OSCAR_SHIPPING_REPOSITORY = 'apps.shipping.repository.Repository'


# Autenticación (Oscar usa Email como usuario por defecto, muy moderno)
AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Haystack (Buscador) - Solr 6.x
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': env('SOLR_URL', default='http://127.0.0.1:8983/solr/xyz_core'),
        'ADMIN_URL': env('SOLR_ADMIN_URL', default='http://127.0.0.1:8983/solr/admin/cores'),
        'INCLUDE_SPELLING': True,
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Configuración de estados de órdenes en Oscar
OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Processed', 'Cancelled',),
    'Being manufactured': ('Shipped', 'Cancelled',),
    'Shipped': ('Delivered',),
    'Delivered': (),
    'Cancelled': (),
}

# Configuración de Tailwind CSS
TAILWIND_APP_NAME = "theme"

# Configuración de IPs internas para el hot-reload
INTERNAL_IPS = [
    "127.0.0.1",
]

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"  # Ajustar según la ruta de npm en Windows

# Email - Para desarrollo, usamos el backend de consola
# Los emails se muestran en la terminal en vez de enviarse
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR / 'tmp' / 'emails'
    OSCAR_FROM_EMAIL = 'noreply@xyzstudio.pe'
    OSCAR_SEND_REGISTRATION_EMAIL = True
# else:
    # Aquí irán tus credenciales de AWS SES, Mailgun o SMTP de Gmail en el futuro
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# =============================================================================
# INFORMACIÓN DE CONTACTO XYZ STUDIO (desde .env)
# =============================================================================
SHOP_WHATSAPP = env('SHOP_WHATSAPP', default='51999999999')
SHOP_EMAIL = env('SHOP_EMAIL', default='contacto@xyzstudio.pe')
SHOP_PHONE = env('SHOP_PHONE', default='999999999')
SHOP_ADDRESS = env('SHOP_ADDRESS', default='Lima, Perú')

# Redes Sociales
SHOP_INSTAGRAM = env('SHOP_INSTAGRAM', default='')
SHOP_TIKTOK = env('SHOP_TIKTOK', default='')
SHOP_LINKEDIN = env('SHOP_LINKEDIN', default='')

# Datos bancarios (sensibles)
BANK_BCP_ACCOUNT = env('BANK_BCP_ACCOUNT', default='')
BANK_BCP_CCI = env('BANK_BCP_CCI', default='')
BANK_BCP_HOLDER = env('BANK_BCP_HOLDER', default='')

# Yape / Plin
YAPE_PHONE = env('YAPE_PHONE', default='')
YAPE_HOLDER = env('YAPE_HOLDER', default='')
PLIN_PHONE = env('PLIN_PHONE', default='')

# Datos legales
LEGAL_NAME = env('LEGAL_NAME', default='David Díaz Malca')
LEGAL_RUC = env('LEGAL_RUC', default='10726400747')