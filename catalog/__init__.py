# coding=utf-8
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

CATALOGS = getattr(settings, 'CATALOGS', None)
CATALOGS_USE_SOCIAL_GRAPH = getattr(settings, 'CATALOGS_USE_SOCIAL_GRAPH', False)

if CATALOGS is None:
    raise ImproperlyConfigured("CATALOGS setting is missing")

MODEL_CONTEXT_TEMPLATES = {}