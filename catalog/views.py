# coding=utf-8
from copy import copy
from django.db.models.query import QuerySet
from django.http import Http404, QueryDict
from django.utils.translation import ugettext as _
try:
    from django.utils.module_loading import import_by_path
except ImportError:
    from django.utils.module_loading import import_string as import_by_path

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
        return {
            'initial': self.get_initial(),
            'data': self.complete_request_dict
        }

    def load_filters(self):
        for filter_name in self.filter_tray:
            filter_obj = self.filter_tray[filter_name]
            if not isinstance(filter_obj, Filter):
                kwargs = filter_obj.setdefault('kwargs', {})
                kwargs.update({
                    'name': filter_name
                })
                filter_obj = import_by_path(filter_obj['type'])(
                    *filter_obj.setdefault('args', []), **kwargs
                )
                self.filter_tray[filter_name] = self.catalog_config['FILTER_TRAY'][filter_name] = filter_obj

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

    def load_sorter(self):
        if self.order_field:
            sorter_name = self.kwargs.setdefault(
                'order_by',  # first from URL kwargs
                self.complete_request_dict.get(self.order_field, None)  # then from REQUEST
            )
            if sorter_name is None or not sorter_name in self.catalog_config['ORDER_BY_OPTIONS']:
                sorter_name = self.default_order

            self.sorter = self.catalog_config['ORDER_BY_OPTIONS'][sorter_name]
            if self.sorter and not isinstance(self.sorter, Sorter):
                self.sorter = self.catalog_config[sorter_name] = import_by_path(self.sorter['type'])(
                    *self.sorter.setdefault('args', []), **self.sorter.setdefault('kwargs', {})
                )

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

        # load filters and sorter
        self.load_filters()
        self.load_sorter()

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
            self.grouper = self.catalog_config[grouper_name] = import_by_path(self.grouper['type'])(
                *self.grouper.setdefault('args', []), **self.grouper.setdefault('kwargs', {})
            )

        self.object_list = self.get_queryset()

        if not self.get_allow_empty():
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(
                    _("Empty list and '%(class_name)s.allow_empty' is False.") % {
                        'class_name': self.__class__.__name__
                    }
                )

        context = self.get_context_data(form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def process_filters(self, querystring):
        self.complete_request_dict = QueryDict(querystring, mutable=True)
        self.complete_request_dict.update(self.get_fixed_filters())

        # load filters
        self.load_filters()

        # instantiate form
        form_class = self.get_form_class()
        if form_class:
            self.form = self.get_form(form_class)
        else:
            self.form = None

        # get valid filters
        filters = {}
        for f in self.filters:
            try:
                f._check_args()
                f.display_as = f.render(self.form)
                filters.update({
                    f.display_as: f
                })
            except (MissingFilterArgument, WrongTypeArgument):
                pass
        return filters

    def get_queryset(self):
        result = super(CatalogView, self).get_queryset().order_by()  # remove previous ordering
        if self.model is None:
            self.model = result.model
        # apply all filters
        for f in self.filters:
            try:
                result = f.filter(result, request=self.request)
                f.fixed = f.name in self.fixed_filters.keys()
                f.applied = True
                f.display_as = f.render(self.form)
            except (MissingFilterArgument, WrongTypeArgument):
                pass
        # then return
        return result

    def get_context_data(self, **kwargs):
        if self.grouper:
            queryset = kwargs.pop('object_list', self.object_list)
            page_size = self.get_paginate_by(queryset)
            max_page = None
            context_object_name = self.get_context_object_name(queryset)
            groups = self.grouper.group(queryset)
            if self.sorter or page_size:  # order and/or pagination stuff
                for group in groups:
                    if self.sorter:
                        queryset = self.sorter.sort(group['object_list'])
                        group.update({
                            'order': self.sorter,
                            'is_sorted': True,
                            'object_list': queryset
                        })
                    if page_size:
                        paginator, page, queryset, is_paginated = self.paginate_queryset(group['object_list'], page_size)
                        group.update({
                            'paginator': paginator,
                            'page_obj': page,
                            'is_paginated': is_paginated,
                            'object_list': queryset
                        })
                        if max_page is None or page.paginator.num_pages > max_page.paginator.num_pages:
                            max_page = page

            context = {
                'grouper': self.grouper,
                'is_grouped': True,
                'object_list': groups,
                'max_page': max_page
            }
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
            'applied_filters': dict([(f.display_as, f) for f in self.filters if f.applied]),
            'result_count': self.object_list.count() if isinstance(self.object_list, QuerySet) else len(self.object_list),
            'request_dict': self.request_dict,
            'query_string': self.request_dict.urlencode(),
            'object_template': self.model.get_object_template(self.view_type)
            if hasattr(self.model, 'get_object_template') else "catalog/no_template.html"
        })
        self.filters = FilterSet()  # reset filters
        return context

    def get_template_names(self):
        return self.catalog_config['VIEW_TYPES'][self.view_type]
