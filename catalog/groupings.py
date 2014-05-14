# coding=utf-8


class Grouping(object):

    def group(self, objects):
        result = dict()
        for obj in objects:
            for group in self.memberships(obj):
                if not str(group) in result:
                    result[str(group)] = {
                        'group_obj': group,
                        'object_list': []
                    }
                result[str(group)]['object_list'].append(obj)
        return result

    def memberships(self, obj):
        return []


class AttributeValueGrouping(Grouping):

    def __init__(self, attribute):
        super(AttributeValueGrouping, self).__init__()
        self.attribute = attribute

    def memberships(self, obj):
        return [getattr(obj, self.attribute)]


class AttributeRangeGrouping(Grouping):

    def __init__(self, attribute, ranges):
        super(AttributeRangeGrouping, self).__init__()
        self.attribute = attribute
        self.ranges = ranges

    def memberships(self, obj):
        for attribute_range in self.ranges:
            if attribute_range[0] < getattr(obj, self.attribute) <= attribute_range[1]:
                return [attribute_range]
        return []