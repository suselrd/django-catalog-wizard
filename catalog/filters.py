# coding=utf-8
from django.db.models.query import QuerySet
from django.db.models import Q
from .exceptions import MissingFilterArgument, WrongTypeArgument


FILTER_NATURE = ['USER', 'OBJECT']  # TODO: think about this!


class Filter(object):
    required_args = []
    arg_types = {}

    def __init__(self):
        super(Filter, self).__init__()
        self.applied = False

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

    def filter(self, objects):
        self._check_args()
        return [obj for obj in objects if self._check(obj)]

    def _check(self, obj):
        return True


class MultipleArgumentFilterMixin(object):
    children = {}


class AttributeValueFilter(Filter):
    required_args = ['value']
    arg_types = {'value': str}

    def __init__(self, attribute, atype=str):
        super(AttributeValueFilter, self).__init__()
        self.attribute = attribute
        if atype != str:
            self.arg_types[self.required_args[0]] = atype

    def filter(self, objects):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__exact" % self.attribute: self.args['value']
            })
        return super(AttributeValueFilter, self).filter(objects)

    def _check(self, obj):
        return getattr(obj, self.attribute) == self.args['value']

    def __unicode__(self):
        return "%s: %s" % (self.attribute, self.args['value'])


class ForeignKeyValueFilter(Filter):
    required_args = ['value']
    arg_types = {'value': int}

    def __init__(self, key):
        super(ForeignKeyValueFilter, self).__init__()
        self.key = key

    def filter(self, objects):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__exact" % self.key: self.args['value']
            })
        return super(ForeignKeyValueFilter, self).filter(objects)

    def _check(self, obj):
        return getattr(obj, self.key) == self.args['value']

    def __unicode__(self):
        return "%s: %s" % (self.key, self.args['value'])


class AttributeContainsFilter(Filter):
    required_args = ['keyword']
    arg_types = {'keyword': str}

    def __init__(self, attribute, case_insensitive=False):
        super(AttributeContainsFilter, self).__init__()
        self.attribute = attribute
        self.insensive = case_insensitive

    def filter(self, objects):
        if isinstance(objects, QuerySet):
            self._check_args()
            if self.insensive:
                lookup_dict = {"%s__icontains" % self.attribute: self.args['keyword']}
            else:
                lookup_dict = {"%s__contains" % self.attribute: self.args['keyword']}
            return objects.filter(Q(**lookup_dict))
        return super(AttributeContainsFilter, self).filter(objects)

    def _check(self, obj):
        return str(getattr(obj, self.attribute)).lower().find(self.args['keyword'].lower()) >= 0

    def __unicode__(self):
        return "%s" % (self.args['keyword'])


class AttributeSetContainsFilter(Filter):
    required_args = ['keyword']
    arg_types = {'keyword': str}

    def __init__(self, *attributes, **kwargs):
        super(AttributeSetContainsFilter, self).__init__()
        self.attributes = list(attributes)
        self.insensive = kwargs.get('case_insensitive', False)

    def filter(self, objects):
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

    def _check(self, obj):
        for attribute in self.attributes:
            if str(getattr(obj, attribute)).lower().find(self.args['keyword'].lower()) >= 0:
                return True
        return False

    def __unicode__(self):
        return "%s" % (self.args['keyword'])


class AttributeMinLimitFilter(Filter):
    required_args = ['min_value']
    arg_types = {'min_value': float}

    def __init__(self, attribute):
        super(AttributeMinLimitFilter, self).__init__()
        self.attribute = attribute

    def filter(self, objects):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__gte" % self.attribute: self.args['min_value']
            })
        return super(AttributeMinLimitFilter, self).filter(objects)

    def _check(self, obj):
        return self.args['min_value'] <= getattr(obj, self.attribute)

    def __unicode__(self):
        return "%s > %s" % (self.attribute, self.args['min_value'])


class AttributeMaxLimitFilter(Filter):
    required_args = ['max_value']
    arg_types = {'max_value': float}

    def __init__(self, attribute):
        super(AttributeMaxLimitFilter, self).__init__()
        self.attribute = attribute

    def filter(self, objects):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__lte" % self.attribute: self.args['max_value']
            })
        return super(AttributeMaxLimitFilter, self).filter(objects)

    def _check(self, obj):
        return getattr(obj, self.attribute) <= self.args['max_value']

    def __unicode__(self):
        return "%s < %s" % (self.attribute, self.args['max_value'])


class AttributeRangeFilter(Filter, MultipleArgumentFilterMixin):
    required_args = ['min_value', 'max_value']
    arg_types = {'min_value': float, 'max_value': float}

    def __init__(self, attribute, children):
        super(AttributeRangeFilter, self).__init__()
        self.attribute = attribute
        self.children = children

    def filter(self, objects):
        if isinstance(objects, QuerySet):
            self._check_args()
            return objects.complex_filter({
                "%s__range" % self.attribute: (self.args['min_value'], self.args['max_value'])
            })
        return super(AttributeRangeFilter, self).filter(objects)

    def _check(self, obj):
        return self.args['min_value'] <= getattr(obj, self.attribute) <= self.args['max_value']

    def __unicode__(self):
        return "%s > %s > %s" % (self.args['max_value'], self.attribute, self.args['min_value'])