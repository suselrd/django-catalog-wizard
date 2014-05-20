# coding=utf-8
from collections import Iterable
from .graph_filters import GraphFilter


class FilterSet(Iterable):

    def __init__(self, filters=None):
        if not filters:
            filters = []
        self.filters = filters

    def add_filter(self, new_filter):
        #  graph filters are applied the last, because of the performance issues
        if isinstance(new_filter, GraphFilter):
            self.filters.append(new_filter)
        else:
            self.filters.insert(0, new_filter)

    def __iter__(self):
        i = 0
        try:
            while True:
                v = self.filters[i]
                yield v
                i += 1
        except IndexError:
            return