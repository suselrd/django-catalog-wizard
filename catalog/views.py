# coding=utf-8
from django.utils.module_loading import import_by_path
from django.views.generic.list import MultipleObjectMixin, ListView

from . import CATALOGS
from .filters import Filter
from .filter_sets import FilterSet


class FilteredListMixin(MultipleObjectMixin):
    filters = FilterSet()

    def get_queryset(self):
        result = super(FilteredListMixin, self).get_queryset()
        if self.model is None:
            self.model = result.model
        for f in self.filters:
            result = f.filter(result)
        return result


class GroupedListMixin(MultipleObjectMixin):
    grouper = None

    def get_context_data(self, **kwargs):
        context = super(GroupedListMixin, self).get_context_data(**kwargs)
        if self.grouper:
            new_object_list = self.grouper.group(context['object_list'])
            context_object_name = self.get_context_object_name(context['object_list'])
            context['object_list'] = new_object_list
            context['is_grouped'] = True
            if context_object_name:
                context[context_object_name] = new_object_list
        return context


class CatalogView(FilteredListMixin, GroupedListMixin, ListView):
    catalog = None

    def __init__(self, **kwargs):
        super(CatalogView, self).__init__(**kwargs)
        if self.catalog:
            self.catalog_config = CATALOGS[self.catalog]
            self.view_type = self.catalog_config['DEFAULT_VIEW_TYPE']
            self.grouping_config = self.catalog_config['DEFAULT_GROUP_BY']

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

        # get group_by
        try:
            self.grouper = self.catalog_config['GROUP_BY_OPTIONS'][self.kwargs['group_by']]
        except KeyError:
            self.grouper = self.catalog_config['GROUP_BY_OPTIONS'][self.grouping_config]

        return super(CatalogView, self).get(request, *args, **kwargs)

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


