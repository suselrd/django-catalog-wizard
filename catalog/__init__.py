# coding=utf-8
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

CATALOGS = getattr(settings, 'CATALOGS', None)

if CATALOGS is None:
    raise ImproperlyConfigured("CATALOGS setting is missing")