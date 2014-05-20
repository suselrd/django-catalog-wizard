# coding=utf-8
from django.utils.module_loading import import_by_path
from django.views.generic.list import ListView
from . import CATALOGS
from .filters import Filter
from .filter_sets import FilterSet
from .groupings import Grouping


class CatalogView(ListView):
    catalog = None

    def __init__(self, **kwargs):
        super(CatalogView, self).__init__(**kwargs)
        if self.catalog:
            self.catalog_config = CATALOGS[self.catalog]
            self.view_type = self.catalog_config['DEFAULT_VIEW_TYPE']
            self.default_grouper = self.catalog_config['DEFAULT_GROUP_BY']
            self.filters = FilterSet()
            self.grouper = None

    def get(self, request, *args, **kwargs):
        self.filters = FilterSet()  # Reset filters
        # get filters
        for filter_name, filter_args in request.GET.iteritems():
            filter_obj = self.catalog_config['FILTER_TRAY'][filter_name]
            if not isinstance(filter_obj, Filter):
                klass = import_by_path(filter_obj['type'])
                args = filter_obj.setdefault('args', [])
                kwargs = filter_obj.setdefault('kwargs', {})
                filter_obj = self.catalog_config['FILTER_TRAY'][filter_name] = klass(*args, **kwargs)

            # ?filter_name=filter_arg_value1, filter_arg_value2
            args = filter_args.split(',')
            filter_obj.set_args(*args)
            self.filters.add_filter(filter_obj)

        # get view_type
        try:
            view_type = self.kwargs['view_type']
            if view_type in self.catalog_config['VIEW_TYPES']:
                self.view_type = view_type
        except KeyError:
            pass

        # get grouper
        grouper_name = self.kwargs.setdefault('group_by', None)
        if grouper_name is None or not grouper_name in self.catalog_config['GROUP_BY_OPTIONS']:
            grouper_name = self.default_grouper
        self.grouper = self.catalog_config['GROUP_BY_OPTIONS'][grouper_name]
        if self.grouper and not isinstance(self.grouper, Grouping):
            klass = import_by_path(self.grouper['type'])
            args = self.grouper.setdefault('args', [])
            kwargs = self.grouper.setdefault('kwargs', {})
            self.grouper = self.catalog_config[grouper_name] = klass(*args, **kwargs)

        return super(CatalogView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        result = super(CatalogView, self).get_queryset()
        if self.model is None:
            self.model = result.model
        # apply all filters
        for f in self.filters:
            result = f.filter(result)
        # then return
        return result

    def get_context_data(self, **kwargs):
        context = super(CatalogView, self).get_context_data(**kwargs)
        if self.grouper:
            context_object_name = self.get_context_object_name(context['object_list'])
            self.groups = self.grouper.group(context['object_list'])
            context['object_list'] = self.groups
            if context_object_name:
                context[context_object_name] = self.groups
            context['is_grouped'] = True
        return context

    def get_template_names(self):
        return self.catalog_config['VIEW_TYPES'][self.view_type]

    def render_to_response(self, context, **response_kwargs):
        if hasattr(self.model, 'get_object_template'):
            object_template = self.model.get_object_template(self.view_type)
        else:
            object_template = "catalog/no_template.html"

        object_specific_templates = {
            'object_template': object_template
        }
        context.update(object_specific_templates)
        return super(CatalogView, self).render_to_response(context, **response_kwargs)


