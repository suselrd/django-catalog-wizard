# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from types import MethodType
from .models import ModelContextTemplate


def catalogue_enabled(cls):
    if len(cls._meta.ordering) > 0:
        raise ImproperlyConfigured("Catalog enable models can't specify an 'ordering' attribute")

    def get_object_template(self, view_type):
        try:
            return ModelContextTemplate.objects.get(model=str(self._meta),
                                                    context=view_type).template
        except ObjectDoesNotExist:
            return "catalog/no_template.html"

    setattr(cls, 'get_object_template', MethodType(get_object_template, cls))
    return cls
