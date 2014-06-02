# coding=utf-8
from django.utils.module_loading import import_by_path
from django.views.generic.list import ListView
from . import CATALOGS
from .filters import Filter
from .filter_sets import FilterSet
from .groupings import Grouping
from .sorters import Sorter


class CatalogView(ListView):
    catalog = None

    def __init__(self, **kwargs):
        super(CatalogView, self).__init__(**kwargs)
        if self.catalog:
            self.catalog_config = CATALOGS[self.catalog]
            self.view_type = self.catalog_config['DEFAULT_VIEW_TYPE']
            self.default_grouper = self.catalog_config['DEFAULT_GROUP_BY']
            self.default_order = self.catalog_config['DEFAULT_ORDER_BY']
            self.filters = FilterSet()
            self.grouper = None
            self.sorter = None

    def get(self, request, *args, **kwargs):
        # get REQUEST dict
        request_dict = {}
        request_dict.update(request.REQUEST)
        # get sorter
        sorter_name = self.kwargs.setdefault('order_by', None)  # first from URL kwargs
        if sorter_name is None:
            sorter_name = request_dict.pop('order_by', None) # then from REQUEST dict
        if sorter_name is None or not sorter_name in self.catalog_config['ORDER_BY_OPTIONS']:
            sorter_name = self.default_order
        self.sorter = self.catalog_config['ORDER_BY_OPTIONS'][sorter_name]
        if self.sorter and not isinstance(self.sorter, Sorter):
            klass = import_by_path(self.sorter['type'])
            args = self.sorter.setdefault('args', [])
            kwargs = self.sorter.setdefault('kwargs', {})
            self.sorter = self.catalog_config[sorter_name] = klass(*args, **kwargs)

        # get filters
        self.filters = FilterSet()  # Reset filters
        for filter_name, filter_args in request_dict.iteritems():
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

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

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
        if self.grouper:
            queryset = kwargs.pop('object_list', self.object_list)
            page_size = self.get_paginate_by(queryset)
            context_object_name = self.get_context_object_name(queryset)
            groups = self.grouper.group(queryset)
            context = {
                'grouper': self.grouper,
                'is_grouped': True
            }
            # paginate
            if page_size:
                for group in groups:
                    paginator, page, queryset, is_paginated = self.paginate_queryset(group['object_list'], page_size)
                    group.update({
                        'paginator': paginator,
                        'page_obj': page,
                        'is_paginated': is_paginated,
                        'object_list': queryset
                    })
            # order
            if self.sorter:
                for group in groups:
                    queryset = self.sorter.sort(group['object_list'])
                    group.update({
                        'order': self.sorter,
                        'is_sorted': True,
                        'object_list': queryset
                    })
            context.update({
                'object_list': groups
            })
            if context_object_name is not None:
                context[context_object_name] = groups
            context.update(kwargs)
        else:
            context = super(CatalogView, self).get_context_data(**kwargs)  # includes pagination stuff
            # order
            if self.sorter:
                queryset = self.sorter.sort(context['object_list'])
                context.update({
                    'order': self.sorter,
                    'is_sorted': True,
                    'object_list': queryset
                })
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


