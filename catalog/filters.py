# coding=utf-8
import datetime
from django.db.models.query import QuerySet
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from .exceptions import MissingFilterArgument, WrongTypeArgument


class Filter(object):
    request_aware = False
    required_args = []
    arg_types = {}

    def __init__(self, **kwargs):
        super(Filter, self).__init__()
        self.applied = False
        self.display_as = ''
        self.name = kwargs.pop('name', None)
        self.label = kwargs.pop('label', None)
        self.tpl = kwargs.pop('tpl', None)
        self.unit = kwargs.pop('unit', None)

    def set_args(self, *args, **kwargs):
        self.args = dict()
        arg_count = 0
        for value in args:
            self.args.setdefault(self.required_args[arg_count], value)
            arg_count += 1
        for key, value in kwargs.iteritems():
            self.args.setdefault(key, value)

    def _check_args(self):  # Check if all required args are supplied
        for arg in self.required_args:
            try:
                self.args[arg] = self.arg_types[arg](self.args[arg])
            except KeyError:
                raise MissingFilterArgument("%s argument is missing" % arg)
            except ValueError:
                raise WrongTypeArgument("%s argument can not be cast to %s" % (arg, self.arg_types[arg]))

    def filter(self, objects, request=None):
        self._check_args()
        return [obj for obj in objects if self._check(obj, request)]

    def _check(self, obj, request=None):
        return True

    def render(self, form=None):
        if not form or not form.is_valid():
            return u"%s" % self
        value = form.cleaned_data[self.name]
        if hasattr(form.fields[self.name], 'choices'):  # it is a choice field
            for key, text in form.fields[self.name].choices:
                if value == key:
                    value = force_text(text)
                    break
        if hasattr(value, '__iter__'):  # it is iterable: a collection of values
            value = u', '.join([force_text(item) for item in value])
        return (self.tpl or u"%s: %s") % (form.fields[self.name].label or self.name, value)


class MultipleArgumentFilterMixin(object):
    children = {}

    def render(self, form=None):
        if not form or not self.tpl or not form.is_valid():
            representation = u"%s" % self
        else:
            representation = self.tpl % dict(
                [(
                    field_name,
                    form.cleaned_data[field_name]
                    if not hasattr(form.cleaned_data[field_name], '__iter__')
                    else u', '.join(  # it is iterable: a collection of values
                        [force_text(item) for item in form.cleaned_data[field_name]])
                ) for field_name, role in self.children.items()]
            )
        if not self.label:
            return representation
        return u"%s: %s" % (force_text(self.label), representation)


class RequestAwareFilterMixin(object):
    request_aware = True

    def filter(self, objects, request=None):
        if self.request_aware and not request:
            raise Exception('Request must be provided to get this filter working.')
        return super(RequestAwareFilterMixin, self).filter(objects)


class AttributeValueFilter(Filter):
    required_args = ['value']
    arg_types = {'value': str}

    def __init__(self, attribute, atype=str, **kwargs):
        super(AttributeValueFilter, self).__init__(**kwargs)
        self.attribute = attribute
        if atype != str:
            self.arg_types[self.required_args[0]] = atype

    def filter(self, objects, request=None):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__exact" % self.attribute: self.args['value']
            })
        return super(AttributeValueFilter, self).filter(objects)

    def _check(self, obj, request=None):
        return getattr(obj, self.attribute) == self.args['value']

    def __unicode__(self):
        return u"%s: %s" % (self.attribute, self.args['value'])


class BoolAttributeValueFilter(AttributeValueFilter):
    arg_types = {'value': bool}

    def _check_args(self):
        for arg in self.required_args:
            try:
                self.args[arg] = (
                    True if self.args[arg] in ('True', '1', True, 1)
                    else False if self.args[arg] in ('False', '0', False, 0)
                    else None
                )
                if self.args[arg] is None:
                    raise MissingFilterArgument("%s argument is missing" % arg)
            except KeyError:
                raise MissingFilterArgument("%s argument is missing" % arg)
            except ValueError:
                raise WrongTypeArgument("%s argument can not be cast to %s" % (arg, self.arg_types[arg]))

    def render(self, form=None):
        if not form or not form.is_valid():
            return u"%s" % self
        value = form.cleaned_data[self.name]
        value = _(u'Yes') if value else _(u'No')
        return (self.tpl or u"%s: %s") % (form.fields[self.name].label or self.name, value)


class ForeignKeyValueFilter(Filter):
    required_args = ['value']
    arg_types = {'value': int}

    def __init__(self, attribute, **kwargs):
        super(ForeignKeyValueFilter, self).__init__(**kwargs)
        self.attribute = attribute

    def filter(self, objects, request=None):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__exact" % self.attribute: self.args['value']
            })
        return super(ForeignKeyValueFilter, self).filter(objects)

    def _check(self, obj, request=None):
        return getattr(obj, self.attribute) == self.args['value']

    def __unicode__(self):
        return u"%s: %s" % (self.attribute, self.args['value'])


class AttributeContainsFilter(Filter):
    required_args = ['keyword']
    arg_types = {'keyword': str}

    def __init__(self, attribute, case_insensitive=False, **kwargs):
        super(AttributeContainsFilter, self).__init__(**kwargs)
        self.attribute = attribute
        self.insensitive = case_insensitive

    def filter(self, objects, request=None):
        if isinstance(objects, QuerySet):
            self._check_args()
            if self.insensitive:
                lookup_dict = {"%s__icontains" % self.attribute: self.args['keyword']}
            else:
                lookup_dict = {"%s__contains" % self.attribute: self.args['keyword']}
            return objects.filter(Q(**lookup_dict))
        return super(AttributeContainsFilter, self).filter(objects)

    def _check(self, obj, request=None):
        return str(getattr(obj, self.attribute)).lower().find(self.args['keyword'].lower()) >= 0

    def __unicode__(self):
        return u"%s" % (self.args['keyword'])


class AttributeSetContainsFilter(Filter):
    required_args = ['keyword']
    arg_types = {'keyword': str}

    def __init__(self, *attributes, **kwargs):
        super(AttributeSetContainsFilter, self).__init__(**kwargs)
        self.attributes = list(attributes)
        self.insensive = kwargs.get('case_insensitive', False)

    def filter(self, objects, request=None):
        if isinstance(objects, QuerySet):
            self._check_args()
            lookup = Q()
            for attribute in self.attributes:
                if self.insensive:
                    lookup_dict = {"%s__icontains" % attribute: self.args['keyword']}
                else:
                    lookup_dict = {"%s__contains" % attribute: self.args['keyword']}
                lookup = lookup | Q(**lookup_dict)
            return objects.filter(lookup)

        return super(AttributeSetContainsFilter, self).filter(objects)

    def _check(self, obj, request=None):
        for attribute in self.attributes:
            if str(getattr(obj, attribute)).lower().find(self.args['keyword'].lower()) >= 0:
                return True
        return False

    def __unicode__(self):
        return u"%s" % (self.args['keyword'])


class AttributeMinLimitFilter(Filter):
    required_args = ['min_value']
    arg_types = {'min_value': float}

    def __init__(self, attribute, **kwargs):
        super(AttributeMinLimitFilter, self).__init__(**kwargs)
        self.attribute = attribute

    def filter(self, objects, request=None):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__gte" % self.attribute: self.args['min_value']
            })
        return super(AttributeMinLimitFilter, self).filter(objects)

    def _check(self, obj, request=None):
        return self.args['min_value'] <= getattr(obj, self.attribute)

    def __unicode__(self):
        return u"%s > %s" % (self.attribute, self.args['min_value'])


class AttributeMaxLimitFilter(Filter):
    required_args = ['max_value']
    arg_types = {'max_value': float}

    def __init__(self, attribute, **kwargs):
        super(AttributeMaxLimitFilter, self).__init__(**kwargs)
        self.attribute = attribute

    def filter(self, objects, request=None):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__lte" % self.attribute: self.args['max_value']
            })
        return super(AttributeMaxLimitFilter, self).filter(objects)

    def _check(self, obj, request=None):
        return getattr(obj, self.attribute) <= self.args['max_value']

    def __unicode__(self):
        return u"%s < %s" % (self.attribute, self.args['max_value'])


class AttributeRangeFilter(MultipleArgumentFilterMixin, Filter):
    required_args = ['min_value', 'max_value']
    arg_types = {'min_value': float, 'max_value': float}

    def __init__(self, attribute, children, **kwargs):
        super(AttributeRangeFilter, self).__init__(**kwargs)
        self.attribute = attribute
        self.children = children

    def filter(self, objects, request=None):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__range" % self.attribute: (self.args['min_value'], self.args['max_value'])
            })
        return super(AttributeRangeFilter, self).filter(objects)

    def _check(self, obj, request=None):
        return self.args['min_value'] <= getattr(obj, self.attribute) <= self.args['max_value']

    def __unicode__(self):
        return u"%s > %s > %s" % (self.args['max_value'], self.attribute, self.args['min_value'])


class DateMixin(object):
    options = {
        'today': {
            'input': (1, '1'),
            'days_back': None,
            'display_as': _(u'today')
        },
        'yesterday': {
            'input': (2, '2'),
            'days_back': 1,
            'display_as': _(u'yesterday')
        },
        'last_week': {
            'input': (3, '3'),
            'days_back': 7,
            'display_as': _(u'last week')
        },
        'last_month': {
            'input': (4, '4'),
            'days_back': 30,
            'display_as': _(u'last month')
        }
    }

    def calculate_arg(self, arg):
        for option in self.options.values():
            if arg in option['input']:
                return (datetime.date.today() - datetime.timedelta(days=option['days_back'])
                        if option['days_back'] else datetime.date.today())
        return None

    def _check_args(self):
        for arg in self.required_args:
            try:
                self.args[arg] = self.calculate_arg(self.args[arg])
                if self.args[arg] is None:
                    raise MissingFilterArgument("%s argument is missing" % arg)

            except KeyError:
                raise MissingFilterArgument("%s argument is missing" % arg)
            except ValueError:
                raise WrongTypeArgument("%s argument can not be cast to %s" % (arg, self.arg_types[arg]))

    def render(self, form=None):
        if not form or not form.is_valid():
            return u"%s" % self
        value = form.cleaned_data[self.name]
        for key, option in self.options.items():
            if value in option['input']:
                return (self.tpl or u"%s: %s") % (
                    form.fields[self.name].label or self.name, option.setdefault('display_as', key)
                )
        return (self.tpl or u"%s: %s") % (form.fields[self.name].label or self.name, value)


class DateAttributeMinLimitFilter(DateMixin, AttributeMinLimitFilter):
    arg_types = {'min_value': datetime.date}


class DateAttributeMaxLimitFilter(DateMixin, AttributeMaxLimitFilter):
    arg_types = {'max_value': datetime.date}


class DateAttributeRangeFilter(DateMixin, AttributeRangeFilter):
    arg_types = {'min_value': datetime.date, 'max_value': datetime.date}
