# coding=utf-8
from abc import abstractmethod
from django.db.models.query import QuerySet


class Sorter(object):

    def __init__(self, attributes):
        if not isinstance(attributes, tuple):
            attributes = (attributes,)
        self.attributes = attributes

    @abstractmethod
    def sort(self, objects):
        return objects

    def _base_sort(self, objects):
        attributes = list()
        for attribute in self.attributes:
            reverse = False
            if attribute[0] == '-':
                reverse = True
                attribute = attribute[1:]
            attributes.append({
                'attr': attribute,
                'reverse': reverse
            })

        def cmp_fn(x, y, i):
            attr_val_x = getattr(x, attributes[i]['attr'])
            attr_val_y = getattr(y, attributes[i]['attr'])
            reverse_factor = -1 if attributes[i]['reverse'] else 1

            if attr_val_x < attr_val_y:
                return -1*reverse_factor
            elif attr_val_x > attr_val_y:
                return 1*reverse_factor
            elif len(attributes) > i+1:
                return cmp_fn(x, y, i+1)
            else:
                return 0

        objects = sorted(objects, lambda x, y: cmp_fn(x, y, 0))
        return objects


class AttributeValueSorter(Sorter):

    def sort(self, objects):
        if isinstance(objects, QuerySet):
            return objects.order_by(*self.attributes)
        return self._base_sort(objects)
