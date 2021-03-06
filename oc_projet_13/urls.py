"""oc_projet_13 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from catalogue import views


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('admin/', admin.site.urls),
    path('catalogue/', include('catalogue.urls')),
    path('', views.IndexView.as_view(),
         {'department_code': '75'}, name='index'),
    path('session/', include('session.urls')),
    path('ventes/', include('ventes.urls')),
    re_path(r'^paypal/', include('paypal.standard.ipn.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
