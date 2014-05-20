# coding=utf-8
from django.conf import settings
from social_graph import EdgeType, EdgeTypeAssociation, Graph

HAVE_VALUE_EDGE_NAME = getattr(settings, 'HAVE_VALUE_EDGE_NAME', None)
DESCRIBED_BY_EDGE_NAME = getattr(settings, 'DESCRIBED_BY_EDGE_NAME', None)


def inverse(edgeType):
    return EdgeTypeAssociation.objects.get(direct=edgeType).inverse


# TODO: reimplement!!!
class GraphGrouping(object):

    def __init__(self):
        super(GraphGrouping, self).__init__()
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
        result['group_list'] = [(key, value['count']) for key, value in result.iteritems()]
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
        self.classifier = classifier
        have_value = EdgeType.objects.get(name=HAVE_VALUE_EDGE_NAME)
        self.described_by = EdgeType.objects.get(name=DESCRIBED_BY_EDGE_NAME)
        count = self.graph.edge_count(classifier, have_value)
        self.groups = set([node for node, attributes, time in self.graph.edge_range(classifier, have_value, 0, count)])

    def memberships(self, obj):
        count = self.graph.edge_count(obj,  self.described_by)
        return set([node for node, attributes, time in self.graph.edge_range(obj,  self.described_by, 0, count)]) & self.groups
