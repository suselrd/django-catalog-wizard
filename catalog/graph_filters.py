# coding=utf-8
from . import CATALOGS_USE_SOCIAL_GRAPH
if CATALOGS_USE_SOCIAL_GRAPH:

    from django.utils.translation import ugettext_lazy as _
    from .filters import Filter, MultipleArgumentFilterMixin

    def inverse(et):
        from social_graph.models import EdgeTypeAssociation
        return EdgeTypeAssociation.objects.get_for_direct_edge_type(et).inverse

    class GraphFilter(Filter):

        def __init__(self, edge_type, target_model, **kwargs):
            super(GraphFilter, self).__init__(**kwargs)

            from social_graph import Graph
            from social_graph.models import EdgeType

            self.graph = Graph()
            self.edge_type = EdgeType.objects.get(name=edge_type)
            self.inverse_edge_type = inverse(self.edge_type)

            if not callable(target_model):
                from django.utils.module_loading import import_by_path
                self.target_model = import_by_path(target_model)
            else:
                self.target_model = target_model

        def _check_args(self):
            super(GraphFilter, self)._check_args()
            try:
                self.args['target_pk'] = self.args['target_pk'].split(',')
            except KeyError:
                pass

    class RelationExistenceFilter(GraphFilter):
        required_args = ['target_pk']
        arg_types = {
            'target_pk': str
        }

        def filter(self, objects, **kwargs):
            self._check_args()
            self.target = list()
            subset = set(objects)
            for target_pk in self.args['target_pk']:
                target = self.target_model.objects.get(pk=target_pk)
                self.target.append(target)
                count = self.graph.edge_count(target, self.inverse_edge_type)
                subset &= set([
                    node for node, attributes, time in self.graph.edge_range(
                        target,
                        self.inverse_edge_type,
                        0,
                        count
                    )
                ])
            return list(subset)

        def __unicode__(self):
            return u"%s %s" % (self.edge_type, self.target)

    class ChildRelationExistenceFilter(GraphFilter):
        required_args = ['target_pk']
        arg_types = {
            'target_pk': str
        }

        def __init__(self, attribute, edge_type, target_model, **kwargs):
            super(ChildRelationExistenceFilter, self).__init__(edge_type, target_model, **kwargs)
            self.attribute = attribute

        def filter(self, objects, **kwargs):
            self._check_args()
            self.target = list()
            subset = set([getattr(obj, self.attribute) for obj in objects])
            for target_pk in self.args['target_pk']:
                target = self.target_model.objects.get(pk=target_pk)
                self.target.append(target)
                count = self.graph.edge_count(target, self.inverse_edge_type)
                subset &= set([
                    node for node, attributes, time in self.graph.edge_range(
                        target,
                        self.inverse_edge_type,
                        0,
                        count
                    )
                ])
            return [obj for obj in objects if getattr(obj, self.attribute) in subset]

        def __unicode__(self):
            return u"%s %s" % (self.edge_type, self.target)

    class RelationAttributeRangeFilter(MultipleArgumentFilterMixin, GraphFilter):
        required_args = ['target_pk', 'min_value', 'max_value']
        arg_types = {
            'target_pk': str,
            'min_value': float,
            'max_value': float
        }

        def __init__(self, edge_type, target_model, attribute, children, **kwargs):
            super(RelationAttributeRangeFilter, self).__init__(edge_type, target_model, **kwargs)
            self.attribute = attribute
            self.children = children

        def filter(self, objects, **kwargs):
            self._check_args()
            self.target = list()
            subset = set(objects)
            for target_pk in self.args['target_pk']:
                target = self.target_model.objects.get(pk=target_pk)
                self.target.append(target)
                count = self.graph.edge_count(target, self.inverse_edge_type)
                subset &= set([
                    node for node, attributes, time in self.graph.edge_range(
                        target,
                        self.inverse_edge_type,
                        0,
                        count
                    ) if self.args['min_value'] <= attributes[self.attribute] <= self.args['max_value']
                ])

            return list(subset)

        def __unicode__(self):
            return u"%s %s (%s < %s < %s)" % (
                self.edge_type,
                self.target,
                self.args['min_value'],
                self.attribute,
                self.args['min_value']
            )

    class ChildRelationAttributeRangeFilter(MultipleArgumentFilterMixin, GraphFilter):
        required_args = ['target_pk', 'min_value', 'max_value']
        arg_types = {
            'target_pk': str,
            'min_value': float,
            'max_value': float
        }

        def __init__(self, object_attribute, edge_type, target_model, attribute, children, **kwargs):
            super(ChildRelationAttributeRangeFilter, self).__init__(edge_type, target_model, **kwargs)
            self.object_attribute = object_attribute
            self.attribute = attribute
            self.children = children

        def filter(self, objects, **kwargs):
            self._check_args()
            self.target = list()
            subset = set([getattr(obj, self.object_attribute) for obj in objects])
            for target_pk in self.args['target_pk']:
                target = self.target_model.objects.get(pk=target_pk)
                self.target.append(target)
                count = self.graph.edge_count(target, self.inverse_edge_type)
                subset &= set([
                    node for node, attributes, time in self.graph.edge_range(
                        target,
                        self.inverse_edge_type,
                        0,
                        count
                    ) if self.args['min_value'] <= attributes[self.attribute] <= self.args['max_value']
                ])
            return [obj for obj in objects if getattr(obj, self.object_attribute) in subset]

        def __unicode__(self):
            return u"%s %s (%s < %s < %s)" % (
                self.edge_type,
                self.target,
                self.args['min_value'],
                self.attribute,
                self.args['min_value']
            )

    class RelationTimeRangeFilter(MultipleArgumentFilterMixin, GraphFilter):
        required_args = ['target_pk', 'min_value', 'max_value']
        arg_types = {
            'target_pk': str,
            'min_value': float,
            'max_value': float
        }

        def __init__(self, edge_type, target_model, children, **kwargs):
            super(RelationTimeRangeFilter, self).__init__(edge_type, target_model, **kwargs)
            self.children = children

        def filter(self, objects, **kwargs):
            self._check_args()
            self.target = list()
            subset = set(objects)
            for target_pk in self.args['target_pk']:
                target = self.target_model.objects.get(pk=target_pk)
                self.target.append(target)
                count = self.graph.edge_count(target, self.inverse_edge_type)
                subset &= set([
                    node for node, attributes, time in self.graph.edge_time_range(
                        target,
                        self.inverse_edge_type,
                        self.args['max_value'],
                        self.args['min_value'],
                        count
                    )
                ])
            return list(subset)

        def __unicode__(self):
            return u"%s %s (%s %s %s %s)" % (
                self.edge_type,
                self.target,
                _(u'from'),
                self.args['min_value'],
                _(u'to'),
                self.args['min_value']
            )

    class ChildRelationTimeRangeFilter(MultipleArgumentFilterMixin, GraphFilter):
        required_args = ['target_pk', 'min_value', 'max_value']
        arg_types = {
            'target_pk': str,
            'min_value': float,
            'max_value': float
        }

        def __init__(self, attribute, edge_type, target_model, children, **kwargs):
            super(ChildRelationTimeRangeFilter, self).__init__(edge_type, target_model, **kwargs)
            self.attribute = attribute
            self.children = children

        def filter(self, objects, **kwargs):
            self._check_args()
            self.target = list()
            subset = set([getattr(obj, self.attribute) for obj in objects])
            for target_pk in self.args['target_pk']:
                target = self.target_model.objects.get(pk=target_pk)
                self.target.append(target)
                count = self.graph.edge_count(target, self.inverse_edge_type)
                subset &= set([
                    node for node, attributes, time in self.graph.edge_time_range(
                        target,
                        self.inverse_edge_type,
                        self.args['max_value'],
                        self.args['min_value'],
                        count
                    )
                ])
            return [obj for obj in objects if getattr(obj, self.attribute) in subset]

        def __unicode__(self):
            return u"%s %s (%s %s %s %s)" % (
                self.edge_type,
                self.target,
                _(u'from'),
                self.args['min_value'],
                _(u'to'),
                self.args['min_value']
            )
