# coding=utf-8
from types import MethodType
from django.core.exceptions import ImproperlyConfigured
from views import CatalogView
from . import MODEL_CONTEXT_TEMPLATES
from models import ModelContextTemplate, SearchLog


def catalogue_enabled_templates(templates=None):
    def decorator(cls):
        tpls = templates or {}
        if not isinstance(tpls, dict):
            raise ImproperlyConfigured("templates argument must be a dict.")
        for view_type, template in tpls.items():
            MODEL_CONTEXT_TEMPLATES.setdefault(str(cls._meta), {}).update({
                view_type: template
            })

        def get_object_template(self, view_type):
            template = MODEL_CONTEXT_TEMPLATES.setdefault(str(self._meta), {}).get(view_type, None)
            if not template:
                try:
                    template = ModelContextTemplate.objects.get(
                        model=str(self._meta),
                        context=view_type
                    ).template
                    MODEL_CONTEXT_TEMPLATES.get(str(self._meta)).setdefault(view_type, template)
                except ModelContextTemplate.DoesNotExist:
                    return "catalog/no_template.html"
            return template

        setattr(cls, 'get_object_template', MethodType(get_object_template, cls))
        return cls
    return decorator


catalogue_enabled = catalogue_enabled_templates()


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
