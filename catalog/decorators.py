# coding=utf-8
from django.core.exceptions import ImproperlyConfigured


def catalogue_enabled_templates(templates=None):
    def decorator(cls):
        from .models import ModelContextTemplate, MODEL_CONTEXT_TEMPLATES_CACHE

        template_list = templates or {}
        if not isinstance(template_list, dict):
            raise ImproperlyConfigured("templates argument must be a dict.")

        for v_type, template in template_list.items():
            MODEL_CONTEXT_TEMPLATES_CACHE.setdefault(str(cls._meta), {}).update({
                v_type: template
            })

        def get_object_template(self, view_type):
            mdt = ModelContextTemplate.objects.get_by_natural_key(
                model=str(self._meta),
                context=view_type
            )
            return mdt.template if mdt else "catalog/no_template.html"

        from types import MethodType
        setattr(cls, 'get_object_template', MethodType(get_object_template, cls))
        return cls
    return decorator


catalogue_enabled = catalogue_enabled_templates()


def log_search(cls):
    from .models import SearchLog
    from .views import CatalogView

    if not issubclass(cls, CatalogView):
        raise ImproperlyConfigured("Only descendants of CatalogView are suitable for search logging.")

    old_method = getattr(cls, 'get')

    def get(self, request, *args, **kwargs):
        result = old_method(self, request, *args, **kwargs)
        SearchLog.objects.create(model=str(self.model._meta), querystring=self.request_dict.urlencode())
        return result

    setattr(cls, 'get', get)
    return cls
