# coding=utf-8
from django.utils.module_loading import import_by_path
from django.utils.translation import ugettext_lazy as _
from social_graph import Graph, EdgeTypeAssociation, EdgeType
from .filters import Filter, MultipleArgumentFilterMixin


def inverse(et):
    return EdgeTypeAssociation.objects.get_for_direct_edge_type(et).inverse


class GraphFilter(Filter):

    def __init__(self, edge_type, target_model):
        super(GraphFilter, self).__init__()
        self.graph = Graph()
        self.edge_type = EdgeType.objects.get(name=edge_type)
        self.inverse_edge_type = inverse(self.edge_type)

        if not callable(target_model):
            self.target_model = import_by_path(target_model)
        else:
            self.target_model = target_model


class RelationExistenceFilter(GraphFilter):
    required_args = ['target_pk']
    arg_types = {
        'target_pk': int
    }

    def filter(self, objects, **kwargs):
        self._check_args()
        self.target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(self.target, self.inverse_edge_type)
        return list(set(objects) & set([node for node, attributes, time in
                                        self.graph.edge_range(self.target,
                                                              self.inverse_edge_type,
                                                              0,
                                                              count)]))

    def __unicode__(self):
        return "%s %s" % (self.edge_type, self.target)


class ChildRelationExistenceFilter(GraphFilter):
    required_args = ['target_pk']
    arg_types = {
        'target_pk': int
    }

    def __init__(self, attribute, edge_type, target_model ):
        super(ChildRelationExistenceFilter, self).__init__(edge_type, target_model)
        self.attribute = attribute

    def filter(self, objects, **kwargs):
        self._check_args()
        self.target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(self.target, self.inverse_edge_type)
        return list(set([getattr(obj, self.attribute) for obj in objects]) & set([node for node, attributes, time in
                                                                                 self.graph.edge_range(self.target,
                                                                                 self.inverse_edge_type,
                                                                                 0,
                                                                                 count)]))

    def __unicode__(self):
        return "%s %s" % (self.edge_type, self.target)


class RelationAttributeRangeFilter(GraphFilter, MultipleArgumentFilterMixin):
    required_args = ['target_pk', 'min_value', 'max_value']
    arg_types = {
        'target_pk': int,
        'min_value': float,
        'max_value': float
    }

    def __init__(self, edge_type, target_model, attribute, children):
        super(RelationAttributeRangeFilter, self).__init__(edge_type, target_model)
        self.attribute = attribute
        self.children = children

    def filter(self, objects, **kwargs):
        self._check_args()
        self.target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(self.target, self.inverse_edge_type)
        return list(set(objects) & set([node for node, attributes, time in
                                        self.graph.edge_range(self.target,
                                                              self.inverse_edge_type,
                                                              0,
                                                              count)
                                        if self.args['min_value'] <= attributes[self.attribute] <= self.args['max_value']]))

    def __unicode__(self):
        return "%s %s (%s < %s < %s)" % (self.edge_type,
                                         self.target,
                                         self.args['min_value'],
                                         self.attribute,
                                         self.args['min_value'])


class ChildRelationAttributeRangeFilter(GraphFilter, MultipleArgumentFilterMixin):
    required_args = ['target_pk', 'min_value', 'max_value']
    arg_types = {
        'target_pk': int,
        'min_value': float,
        'max_value': float
    }

    def __init__(self, object_attribute, edge_type, target_model, attribute, children):
        super(ChildRelationAttributeRangeFilter, self).__init__(edge_type, target_model)
        self.object_attribute = object_attribute
        self.attribute = attribute
        self.children = children

    def filter(self, objects, **kwargs):
        self._check_args()
        self.target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(self.target, self.inverse_edge_type)
        return list(set([getattr(obj, self.object_attribute) for obj in objects]) & set([node for node, attributes, time in
                                                                                        self.graph.edge_range(self.target,
                                                                                                              self.inverse_edge_type,
                                                                                                              0,
                                                                                                              count)
                                                                                        if self.args['min_value'] <= attributes[self.attribute] <= self.args['max_value']]))

    def __unicode__(self):
        return "%s %s (%s < %s < %s)" % (self.edge_type,
                                         self.target,
                                         self.args['min_value'],
                                         self.attribute,
                                         self.args['min_value'])


class RelationTimeRangeFilter(GraphFilter, MultipleArgumentFilterMixin):
    required_args = ['target_pk', 'min_value', 'max_value']
    arg_types = {
        'target_pk': int,
        'min_value': float,
        'max_value': float
    }

    def __init__(self, edge_type, target_model, children):
        super(RelationTimeRangeFilter, self).__init__(edge_type, target_model)
        self.children = children

    def filter(self, objects, **kwargs):
        self._check_args()
        self.target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(self.target, self.inverse_edge_type)
        return list(set(objects) & set([node for node, attributes, time in
                                        self.graph.edge_time_range(self.target,
                                                                   self.inverse_edge_type,
                                                                   self.args['max_value'],
                                                                   self.args['min_value'],
                                                                   count)]))

    def __unicode__(self):
        return "%s %s (%s %s %s %s)" % (self.edge_type,
                                         self.target,
                                         _('from'),
                                         self.args['min_value'],
                                         _('to'),
                                         self.args['min_value'])


class ChildRelationTimeRangeFilter(GraphFilter, MultipleArgumentFilterMixin):
    required_args = ['target_pk', 'min_value', 'max_value']
    arg_types = {
        'target_pk': int,
        'min_value': float,
        'max_value': float
    }

    def __init__(self, attribute, edge_type, target_model, children):
        super(ChildRelationTimeRangeFilter, self).__init__(edge_type, target_model)
        self.attribute = attribute
        self.children = children

    def filter(self, objects, **kwargs):
        self._check_args()
        self.target = self.target_model.objects.get(pk=self.args['target_pk'])
        count = self.graph.edge_count(self.target, self.inverse_edge_type)
        return list(set([getattr(obj, self.attribute) for obj in objects]) & set([node for node, attributes, time in
                                                                                 self.graph.edge_time_range(self.target,
                                                                                                            self.inverse_edge_type,
                                                                                                            self.args['max_value'],
                                                                                                            self.args['min_value'],
                                                                                                            count)]))

    def __unicode__(self):
        return "%s %s (%s %s %s %s)" % (self.edge_type,
                                         self.target,
                                         _('from'),
                                         self.args['min_value'],
                                         _('to'),
                                         self.args['min_value'])