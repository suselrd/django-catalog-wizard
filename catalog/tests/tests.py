# coding=utf-8
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from social_graph import EdgeType, Graph
from .models import PropertyPublication


class TestCatalog(TestCase):
    fixtures = ['test_data.json']

    def test_basics(self):
        c = Client()
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }))
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 2)

        data = {
            'operation_type': 1  # SALE
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        data = {
            'budget_min': 7000
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        data = {
            'budget_max': 7000
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        data = {
            'budget_max': 7000,
            'budget_min': 6000
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 0)

        data = {
            'name': 'Property 1'
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        data = {
            'name_contains': 'Property'
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 2)

        data = {
            'keyword': 'Property'
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 2)

        data = {
            'keyword': 'bla'
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        data = {
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'owner'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)
        self.assertEqual(len(response.context_data['object_list'][0]['object_list']), 2)

        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ownername'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)
        self.assertEqual(len(response.context_data['object_list'][0]['object_list']), 2)

    def test_relation_existence_filter(self):
        article = PropertyPublication.objects.get(pk=1)
        user = User.objects.get(pk=1)
        like = EdgeType.objects.get(pk=1)
        Graph().edge_add(user, article, like)
        c = Client()
        data = {
            'liked_by': 1
        }
        # test without grouping first
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        # then, test with grouping
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'status'
        }), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)
        self.assertEqual(len(response.context_data['object_list'][0]['object_list']), 1)

    def test_relation_attribute_range_filter(self):
        pass

    def test_relation_time_range_filter(self):
        pass

    def test_custom_filter(self):
        pass

    def test_relation_target_grouping(self):
        pass

    def test_classifier_grouping(self):
        pass

    def test_custom_grouping(self):
        pass