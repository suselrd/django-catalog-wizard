# coding=utf-8
import datetime
import time
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from social_graph import EdgeType, Graph
from .models import PropertyPublication


class TestCatalog(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.time0 = datetime.datetime.now()
        self.user = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.user3 = User.objects.get(pk=3)
        self.article = PropertyPublication.objects.get(pk=1)
        self.like = EdgeType.objects.get(pk=1)
        Graph().edge_add(self.user, self.article, self.like)
        Graph().edge_add(self.user3, self.article, self.like)

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

        data = {
            'order_by': 'price_asc'
        }

        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ownername'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)
        self.assertEqual(len(response.context_data['object_list'][0]['object_list']), 2)
        self.assertEqual(response.context_data['object_list'][0]['object_list'][0].price, 500)
        self.assertEqual(response.context_data['is_grouped'], True)
        self.assertEqual(response.context_data['object_list'][0]['is_sorted'], True)

        data = {
            'order_by': 'price_desc'
        }

        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ownername'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)
        self.assertEqual(len(response.context_data['object_list'][0]['object_list']), 2)
        self.assertEqual(response.context_data['object_list'][0]['object_list'][0].price, 10000)
        self.assertEqual(response.context_data['is_grouped'], True)
        self.assertEqual(response.context_data['object_list'][0]['is_sorted'], True)

        data = {
            'order_by': 'complex_order'
        }

        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ownername'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)
        self.assertEqual(len(response.context_data['object_list'][0]['object_list']), 2)
        self.assertEqual(response.context_data['object_list'][0]['object_list'][0].price, 500)
        self.assertEqual(response.context_data['is_grouped'], True)
        self.assertEqual(response.context_data['object_list'][0]['is_sorted'], True)

    def test_relation_existence_filter(self):
        c = Client()
        data = {
            'liked_by': "1"
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

        # test with multi-target
        data = {
            'liked_by': "1,2"
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 0)

        data = {
            'liked_by': "1,3"
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

    def test_relation_attribute_range_filter(self):
        pass

    def test_relation_time_range_filter(self):
        c = Client()
        data = {
            'liked_by_target': "1",
            'liked_by_from': time.mktime(self.time0.timetuple()),
            'liked_by_to':  time.mktime(datetime.datetime.now().timetuple())
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        # test with multi-target
        data = {
            'liked_by_target': "1,2",
            'liked_by_from': time.mktime(self.time0.timetuple()),
            'liked_by_to':  time.mktime(datetime.datetime.now().timetuple())
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 0)

        data = {
            'liked_by_target': "1,3",
            'liked_by_from': time.mktime(self.time0.timetuple()),
            'liked_by_to':  time.mktime(datetime.datetime.now().timetuple())
        }
        response = c.get(reverse('property_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

    def test_custom_filter(self):
        pass

    def test_relation_target_grouping(self):
        pass

    def test_classifier_grouping(self):
        pass

    def test_custom_grouping(self):
        pass

    def test_template_tag(self):
        c = Client()
        response = c.get(reverse('detail', kwargs={
            'pk': 1,
        }))
        self.assertEqual(response.status_code, 200)
        self.assertIn('object', response.context_data)
        self.assertHTMLEqual("tests/grid.html", response.content)

    def test_fixed_filters(self):
        c = Client()

        response = c.get(reverse('property_sales_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }))

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

    def test_search_logging(self):
        c = Client()

        data = {
            'budget_min': 7000
        }

        response = c.get(reverse('property_sales_catalog', kwargs={
            'view_type': 'grid',
            'group_by': 'ungrouped'
        }), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context_data)
        self.assertEqual(len(response.context_data['object_list']), 1)

        from catalog.models import SearchLog
        self.assertEqual(SearchLog.objects.count(), 1)
        self.assertEqual(SearchLog.objects.all()[0].model, "tests.propertypublication")
        self.assertEqual(SearchLog.objects.all()[0].querystring, "budget_min=7000")

