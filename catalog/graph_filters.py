# coding=utf-8
from django.core.exceptions import ImproperlyConfigured
from social_graph import Graph, EdgeTypeAssociation, EdgeType
from .filters import Filter


def inverse(et):
    return EdgeTypeAssociation.objects.get_for_direct_edge_type(et).inverse


class GraphFilter(Filter):

    def __init__(self):
        super(GraphFilter, self).__init__()
        self.graph = Graph()


class RelationExistenceFilter(GraphFilter):
    required_args = ['target_pk']
    arg_types = {
        'target_pk': int
    }

    def __init__(self, edge_type, target_model):
        super(RelationExistenceFilter, self).__init__()
        self.edge_type = EdgeType.objects.get(name=edge_type)
        self.inverse_edge_type = inverse(self.edge_type)

        if not callable(target_model):
            module_parts = target_model.split('.')
            module = ".".join(module_parts[:-1])
            try:
                result = __import__(module)
                for component in module_parts[1:]:
                    result = getattr(result, component)
            except (ImportError, Exception) as e:
                raise ImproperlyConfigured("Invalid target_model argument")
            self.target_model = result
        else:
            self.target_model = target_model

    def filter(self, objects, **kwargs):
        self._check_args()
        target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(target, self.inverse_edge_type)
        return list(set(objects) & set([node for node, attributes, time in
                                        self.graph.edge_range(target,
                                                              self.inverse_edge_type,
                                                              0,
                                                              count)]))


class RelationAttributeRangeFilter(GraphFilter):
    required_args = ['target_pk', 'min_value', 'max_value']
    arg_types = {
        'target_pk': int,
        'min_value': float,
        'max_value': float
    }

    def __init__(self, edge_type, attribute, target_model):
        super(RelationAttributeRangeFilter, self).__init__()
        self.edge_type = EdgeType.objects.get(name=edge_type)
        self.inverse_edge_type = inverse(self.edge_type)
        self.attribute = attribute

        if not callable(target_model):
            module_parts = target_model.split('.')
            module = ".".join(module_parts[:-1])
            try:
                result = __import__(module)
                for component in module_parts[1:]:
                    result = getattr(result, component)
            except (ImportError, Exception) as e:
                raise ImproperlyConfigured("Invalid target_model argument")
            self.target_model = result
        else:
            self.target_model = target_model

    def filter(self, objects, **kwargs):
        self._check_args()
        target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(target, self.inverse_edge_type)
        return list(set(objects) & set([node for node, attributes, time in
                                        self.graph.edge_range(target,
                                                              self.inverse_edge_type,
                                                              0,
                                                              count)
                                        if self.args['min_value'] <= attributes[self.attribute] <= self.args['max_value']]))


class RelationTimeRangeFilter(GraphFilter):
    required_args = ['target_pk', 'min_value', 'max_value']
    arg_types = {
        'target_pk': int,
        'min_value': float,
        'max_value': float
    }

    def __init__(self, edge_type, target_model):
        super(RelationTimeRangeFilter, self).__init__()
        self.edge_type = EdgeType.objects.get(name=edge_type)
        self.inverse_edge_type = inverse(self.edge_type)

        if not callable(target_model):
            module_parts = target_model.split('.')
            module = ".".join(module_parts[:-1])
            try:
                result = __import__(module)
                for component in module_parts[1:]:
                    result = getattr(result, component)
            except (ImportError, Exception) as e:
                raise ImproperlyConfigured("Invalid target_model argument")
            self.target_model = result
        else:
            self.target_model = target_model

    def filter(self, objects, **kwargs):
        self._check_args()
        target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(target, self.inverse_edge_type)
        return list(set(objects) & set([node for node, attributes, time in
                                        self.graph.edge_time_range(target,
                                                                   self.inverse_edge_type,
                                                                   self.args['max_value'],
                                                                   self.args['min_value'],
                                                                   count)]))