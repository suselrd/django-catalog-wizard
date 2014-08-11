# coding=utf-8
from copy import copy
from django.http import Http404
from django.utils.translation import ugettext as _
from django.utils.module_loading import import_by_path
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView
from . import CATALOGS
from .filters import Filter, MultipleArgumentFilterMixin
from .filter_sets import FilterSet
from .groupings import Grouping
from .sorters import Sorter
from .exceptions import MissingFilterArgument, WrongTypeArgument


class CatalogView(ListView, FormMixin):
    catalog = None
    order_field = 'order_by'
    fixed_filters = {}

    def __init__(self, **kwargs):
        super(CatalogView, self).__init__(**kwargs)
        if self.catalog:
            self.catalog_config = CATALOGS[self.catalog]
            self.view_type = self.catalog_config['DEFAULT_VIEW_TYPE']
            self.default_grouper = self.catalog_config['DEFAULT_GROUP_BY']
            self.default_order = self.catalog_config['DEFAULT_ORDER_BY']
            self.filter_tray = self.catalog_config['FILTER_TRAY']
            self.filters = FilterSet()
            self.grouper = None
            self.sorter = None

    def get_fixed_filters(self):
        """
        Overwriting methods must return a dict (supports MultiValueDict) specifying values for fixed filters
        """
        return self.fixed_filters

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        for filter_name in self.filter_tray:
            filter_obj = self.filter_tray[filter_name]
            if not isinstance(filter_obj, Filter):
                klass = import_by_path(filter_obj['type'])
                args = filter_obj.setdefault('args', [])
                kwargs = filter_obj.setdefault('kwargs', {})
                filter_obj = self.filter_tray[filter_name] = self.catalog_config['FILTER_TRAY'][filter_name] = klass(*args, **kwargs)

            if isinstance(filter_obj, MultipleArgumentFilterMixin):
                children = filter_obj.children
                children_values = {}
                for child, role in children.iteritems():
                    child_value = self.complete_request_dict.get(child)
                    if child_value:
                        children_values[role] = child_value
                if len(children_values) == len(filter_obj.required_args):
                    filter_obj.set_args(**children_values)
                    self.filters.add_filter(filter_obj)
            else:
                value = self.complete_request_dict.getlist(filter_name)
                value = [val for val in value if val]
                if value:
                    value = ",".join(value)
                    filter_obj.set_args(value)
                    self.filters.add_filter(filter_obj)

        if self.order_field:
            sorter_name = self.kwargs.setdefault('order_by',  # first from URL kwargs
                                                 self.complete_request_dict.get(self.order_field, None))  # then from REQUEST
            if sorter_name is None or not sorter_name in self.catalog_config['ORDER_BY_OPTIONS']:
                sorter_name = self.default_order

            self.sorter = self.catalog_config['ORDER_BY_OPTIONS'][sorter_name]
            if self.sorter and not isinstance(self.sorter, Sorter):
                klass = import_by_path(self.sorter['type'])
                args = self.sorter.setdefault('args', [])
                kwargs = self.sorter.setdefault('kwargs', {})
                self.sorter = self.catalog_config[sorter_name] = klass(*args, **kwargs)

        return {'initial': self.get_initial(),
                'data': self.complete_request_dict}

    def get(self, request, *args, **kwargs):
        # get REQUEST dict
        self.request_dict = copy(request.GET) if len(request.GET) else copy(request.POST)
        self.request_dict.pop('page', None)

        # create a copy of the request_dict, for add the fixed filters to it
        self.complete_request_dict = copy(self.request_dict)
        self.complete_request_dict.update(self.get_fixed_filters())

        # instantiate form
        form_class = self.get_form_class()
        if form_class:
            self.form = self.get_form(form_class)
        else:
            self.form = None

        #get view_type
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

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})
        context = self.get_context_data(form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        result = super(CatalogView, self).get_queryset()
        if self.model is None:
            self.model = result.model
        # apply all filters
        for f in self.filters:
            try:
                result = f.filter(result)
                f.applied = True
            except (MissingFilterArgument, WrongTypeArgument):
                pass
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
            # order
            if self.sorter:
                for group in groups:
                    queryset = self.sorter.sort(group['object_list'])
                    group.update({
                        'order': self.sorter,
                        'is_sorted': True,
                        'object_list': queryset
                    })
            # paginate
            if page_size:
                max_page = None
                for group in groups:
                    paginator, page, queryset, is_paginated = self.paginate_queryset(group['object_list'], page_size)
                    group.update({
                        'paginator': paginator,
                        'page_obj': page,
                        'is_paginated': is_paginated,
                        'object_list': queryset
                    })
                    if max_page is None or page.paginator.num_pages > max_page.paginator.num_pages:
                        max_page = page
                context.update({
                    'max_page': max_page
                })

            context.update({
                'object_list': groups
            })
            if context_object_name is not None:
                context[context_object_name] = groups
            context.update(kwargs)
        else:
            # order
            if self.sorter:
                queryset = kwargs.pop('object_list', self.object_list)
                queryset = self.sorter.sort(queryset)
                kwargs.update({
                    'order': self.sorter,
                    'is_sorted': True,
                    'object_list': queryset
                })
            context = super(CatalogView, self).get_context_data(**kwargs)  # includes pagination stuff

        context.update({
            'applied_filters': [f for f in self.filters if f.applied],
            'request_dict': self.request_dict,
            'query_string': self.request_dict.urlencode()
        })
        self.filters = FilterSet()  # reset filters
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


