# coding=utf-8
from abc import abstractmethod
from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.db.models.aggregates import Sum, Avg, Count, Max, Min

AGGREGATION_TYPES = {
    'Count': Count,
    'Sum': Sum,
    'Avg': Avg,
    'Min': Min,
    'Max': Max,
}


class Grouping(object):

    def __init__(self, attribute, aggregate=None):
        self.attribute = attribute
        self.aggregate = aggregate if aggregate else {}

    @abstractmethod
    def group(self, objects):
        return {}

    def _base_group(self, objects):
        result = dict()
        if self.aggregate:
            aggregates = dict()
            aggregation_functions = dict([(value['type'], key) for key, value in self.aggregate.iteritems()])
        for obj in objects:
            attr = getattr(obj, self.attribute)
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

        for group_key, group in result.iteritems():
            for key, value in self.aggregate.iteritems():
                if value['type'] == 'Avg':
                    key_value = aggregates[group_key]['Sum']/aggregates[group_key]['Count']
                else:
                    key_value = aggregates[group_key][value['type']]
                result[group_key].update({key: key_value})

        return [value for value in result.values()]


class AttributeValueGrouping(Grouping):

    def group(self, objects):
        if isinstance(objects, QuerySet):
            result = objects.select_related().values(self.attribute)
            if self.aggregate:
                aggregate_dict = dict([(key, AGGREGATION_TYPES[value['type']](value['attribute']))
                                       for key, value in self.aggregate.iteritems()])
                result = result.annotate(**aggregate_dict)

            for group in result:
                lookup_dict = {
                    self.attribute: group[self.attribute]
                }
                group['object_list'] = objects.filter(**lookup_dict)
            return result
        return self._base_group(objects)