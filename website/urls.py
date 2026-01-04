"""
URL configuration for website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.apps import apps
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='oscar/promotions/home.html'), name='home'),
    path('sobre-xyz/', TemplateView.as_view(template_name='oscar/pages/sobre_xyz.html'), name='sobre-xyz'),
    path('politica-de-envios/', TemplateView.as_view(template_name='oscar/pages/politica_envios.html'), name='politica-envios'),
    path('politica-de-privacidad/', TemplateView.as_view(template_name='oscar/pages/privacy_policy.html'), name='politica-privacidad'),
    path('terminos-condiciones/', TemplateView.as_view(template_name='oscar/pages/terminos_condiciones.html'), name='terminos-condiciones'),
    path('cuidado-pla/', TemplateView.as_view(template_name='oscar/pages/cuidado_pla.html'), name='cuidado-pla'),
    path('', include(apps.get_app_config('oscar').urls[0])),
]

# Esto asegura que las fotos se vean mientras desarrollas
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]