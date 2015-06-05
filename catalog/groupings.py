# coding=utf-8
from abc import abstractmethod
from django.db.models.query import QuerySet
from django.db.models.aggregates import Sum, Avg, Count, Max, Min
from django.utils import dateformat

AGGREGATION_TYPES = {
    'Count': Count,
    'Sum': Sum,
    'Avg': Avg,
    'Min': Min,
    'Max': Max,
}


class Grouping(object):
    group_by = None
    attribute_aliases = []
    additional_data = None

    def __init__(self, attribute, aggregate=None):
        self.attribute = attribute
        self.aggregate = aggregate if aggregate else {}

    def get_group_name(self, group):
        """
        Overwriting methods must return a string
        """
        return '%s' % group[self.attribute]

    def get_group_by_name(self):
        """
        Overwriting methods must return a string
        """
        return self.group_by or self.attribute

    def get_additional_data(self, group):
        """
        Overwriting methods must return a string
        """
        return self.additional_data or {}

    def get_attribute(self, obj):
        return getattr(obj, self.attribute)

    @abstractmethod
    def group(self, objects):
        return {}

    def _base_group(self, objects):
        result = dict()
        if self.aggregate:
            aggregates = dict()
            aggregation_functions = dict([(value['type'], key) for key, value in self.aggregate.items()])
        for obj in objects:
            attr = self.get_attribute(obj)
            if not str(attr) in result:
                result[str(attr)] = {
                    self.attribute: attr,
                    'object_list': [],
                }
            result[str(attr)]['object_list'].append(obj)
            if self.aggregate:
                functions = aggregation_functions.keys()
                if 'Count' in functions or 'Avg' in functions:
                    aggregates.setdefault(str(attr), {}).setdefault('Count', 0)
                    aggregates[str(attr)]['Count'] += 1
                if 'Sum' in functions or 'Avg' in functions:
                    aggregates.setdefault(str(attr), {}).setdefault('Sum', 0)
                    try:
                        field = self.aggregate[aggregation_functions['Sum']]['attribute']
                    except KeyError:
                        field = self.aggregate[aggregation_functions['Avg']]['attribute']
                    aggregates[str(attr)]['Sum'] += getattr(obj, field)
                if 'Min' in functions:
                    current_min = aggregates.setdefault(str(attr), {}).setdefault('Min', None)
                    field = self.aggregate[aggregation_functions['Min']]['attribute']
                    field_value = getattr(obj, field)
                    if current_min is None or field_value < current_min:
                        aggregates[str(attr)]['Min'] = field_value
                if 'Max' in functions:
                    current_min = aggregates.setdefault(str(attr), {}).setdefault('Min', None)
                    field = self.aggregate[aggregation_functions['Max']]['attribute']
                    field_value = getattr(obj, field)
                    if current_min is None or field_value < current_min:
                        aggregates[str(attr)]['Max'] = field_value

        for group_key, group in result.items():
            result[group_key].update({
                'name': self.get_group_name(group),
                'group_by': self.get_group_by_name()
            })
            for alias in self.attribute_aliases:
                result[group_key].update({
                    alias: group[self.attribute]
                })
            for additional_key, additional_value in self.get_additional_data(group).items():
                result[group_key].update({
                    additional_key: additional_value
                })
            for key, value in self.aggregate.items():
                if value['type'] == 'Avg':
                    key_value = aggregates[group_key]['Sum']/aggregates[group_key]['Count']
                else:
                    key_value = aggregates[group_key][value['type']]
                result[group_key].update({key: key_value})

        return result.values()


class AttributeValueGrouping(Grouping):

    def get_groups(self, objects):
        result = objects.select_related().values(self.attribute)
        if self.aggregate:
            result = result.annotate(
                **dict([(
                    key, AGGREGATION_TYPES[value['type']](value['attribute']))
                    for key, value in self.aggregate.items()
                ])
            )
        return result

    def get_lookup_dict(self, group):
        return {
            self.attribute: group[self.attribute]
        }

    def group(self, objects):
        if isinstance(objects, QuerySet):
            result = self.get_groups(objects)
            for group in result:
                group['object_list'] = objects.filter(**self.get_lookup_dict(group))
                group['name'] = self.get_group_name(group)
                group['group_by'] = self.get_group_by_name()
                for alias in self.attribute_aliases:
                    group.update({
                        alias: group[self.attribute]
                    })
                for additional_key, additional_value in self.get_additional_data(group).items():
                    group.update({
                        additional_key: additional_value
                    })
            return result
        return self._base_group(objects)


class DateTimeMixin(object):

    def get_groups(self, objects):
        return [
            {self.attribute: value} for value in objects.select_related().datetimes(self.attribute, self.group_by)
        ]


class DateAttributeValueGrouping(AttributeValueGrouping):
    group_by = 'day'
    output_format = 'j F Y'
    attribute_aliases = ['date']

    def get_lookup_dict(self, group):
        return {
            '%s__day' % self.attribute: group[self.attribute].day,
            '%s__month' % self.attribute: group[self.attribute].month,
            '%s__year' % self.attribute: group[self.attribute].year
        }

    def get_additional_data(self, group):
        result = super(DateAttributeValueGrouping, self).get_additional_data(group)
        if self.aggregate:
            result.update(
                group['object_list'].aggregate(
                    **dict([
                        (key, AGGREGATION_TYPES[value['type']](value['attribute']))
                        for key, value in self.aggregate.items()
                    ])
                )
            )
        return result

    def get_groups(self, objects):
        return [
            {self.attribute: value} for value in objects.select_related().dates(self.attribute, self.group_by)
        ]

    def get_group_name(self, group):
        return '%s' % (dateformat.DateFormat(group[self.attribute]).format(self.output_format))


class DateTimeAttributeValueGrouping(DateTimeMixin, DateAttributeValueGrouping):
    pass


class DateAttributeMonthValueGrouping(DateAttributeValueGrouping):
    group_by = 'month'
    output_format = 'F Y'

    def get_lookup_dict(self, group):
        return {
            '%s__month' % self.attribute: group[self.attribute].month,
            '%s__year' % self.attribute: group[self.attribute].year
        }


class DateTimeAttributeMonthValueGrouping(DateTimeMixin, DateAttributeMonthValueGrouping):
    pass


class DateAttributeYearValueGrouping(DateAttributeValueGrouping):
    group_by = 'year'
    output_format = 'Y'

    def get_lookup_dict(self, group):
        return {
            '%s__year' % self.attribute: group[self.attribute].year
        }


class DateTimeAttributeYearValueGrouping(DateTimeMixin, DateAttributeYearValueGrouping):
    pass
