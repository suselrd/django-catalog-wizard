# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from types import MethodType
from .views import CatalogView
from .models import ModelContextTemplate, SearchLog


def catalogue_enabled(cls):
    if len(cls._meta.ordering) > 0:
        raise ImproperlyConfigured("Catalog enable models can't specify an 'ordering' attribute.")

    def get_object_template(self, view_type):
        try:
            return ModelContextTemplate.objects.get(model=str(self._meta),
                                                    context=view_type).template
        except ObjectDoesNotExist:
            return "catalog/no_template.html"

    setattr(cls, 'get_object_template', MethodType(get_object_template, cls))
    return cls


def log_search(cls):
    if not issubclass(cls, CatalogView):
        raise ImproperlyConfigured("Only descendants of CatalogView are suitable for search logging.")

    old_method = getattr(cls, 'get')

    def get(self, request, *args, **kwargs):
        result = old_method(self, request, *args, **kwargs)
        SearchLog.objects.create(model=str(self.model._meta), querystring=self.request_dict.urlencode())
        return result

    setattr(cls, 'get', get)
    return cls
