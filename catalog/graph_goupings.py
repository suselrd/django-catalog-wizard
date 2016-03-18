# coding=utf-8
from . import CATALOGS_USE_SOCIAL_GRAPH
if CATALOGS_USE_SOCIAL_GRAPH:

    from django.conf import settings


    def inverse(edge_type):
        from social_graph.models import EdgeTypeAssociation
        return EdgeTypeAssociation.objects.get(direct=edge_type).inverse


    # TODO: re-implement!!!
    class GraphGrouping(object):

        def __init__(self):
            super(GraphGrouping, self).__init__()
            from social_graph import Graph
            self.graph = Graph()

        def group(self, objects):
            result = dict()
            for obj in objects:
                for group in self.memberships(obj):
                    if not str(group) in result:
                        result[str(group)] = {
                            'group_obj': group,
                            'object_list': [],
                            'count': 0
                        }
                    result[str(group)]['object_list'].append(obj)
                    result[str(group)]['count'] += 1
            result['group_list'] = [(key, value['count']) for key, value in result.items()]
            return result

        def memberships(self, obj):
            return []


    class RelationTargetGrouping(GraphGrouping):

        def __init__(self, edge_type):
            super(RelationTargetGrouping, self).__init__()
            self.edge_type = edge_type

        def memberships(self, obj):
            count = self.graph.edge_count(obj, self.edge_type)
            return [node for node, attributes, time in self.graph.edge_range(obj, self.edge_type, 0, count)]


    class ClassifierGrouping(GraphGrouping):

        def __init__(self, classifier):
            super(ClassifierGrouping, self).__init__()

            from social_graph.models import EdgeType
            have_value_edge_name = getattr(settings, 'HAVE_VALUE_EDGE_NAME', None)
            described_by_edge_name = getattr(settings, 'DESCRIBED_BY_EDGE_NAME', None)

            self.classifier = classifier
            have_value = EdgeType.objects.get(name=have_value_edge_name)
            self.described_by = EdgeType.objects.get(name=described_by_edge_name)
            count = self.graph.edge_count(classifier, have_value)
            self.groups = set(
                [node for node, attributes, time in self.graph.edge_range(classifier, have_value, 0, count)]
            )

        def memberships(self, obj):
            count = self.graph.edge_count(obj,  self.described_by)
            return set([
                node for node, attributes, time in self.graph.edge_range(obj,  self.described_by, 0, count)
            ]) & self.groups
