"""demo_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from __future__ import absolute_import
from django.conf.urls import include, url
from django.contrib import admin
from infi.django_rest_utils import routers
import django

from . import views


router = routers.DefaultRouter(
    name='TEST API',
    description=''
)

router.register(r'allfields', views.AllFieldsDataView, basename='allfields')
router.register(r'partialfields', views.PartialFieldsDataView, basename='partialfields')
router.register(r'excludefields', views.ExcludeFieldsDataView, basename='excludefields')
router.register(r'filterablefields', views.SpecificFiltersDataView, basename='filterablefields')

if django.VERSION[0] == '1':
    urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^api/rest/', include(router.urls))
    ]
else:
    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^api/rest/', include(router.urls))
    ]
