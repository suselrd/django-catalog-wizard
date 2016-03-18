# coding=utf-8
from django.conf.urls import patterns, url
from django.views.generic import DetailView
from catalog.views import CatalogView
from .models import PropertyPublication, Test
from .forms import FilterForm
from .views import PropertySalesCatalogView


urlpatterns = patterns(
    "",
    url(
        r"^sales/(?P<view_type>[A-Za-z]+)/(?P<group_by>[A-Za-z]+)/$",
        PropertySalesCatalogView.as_view(),
        name="property_sales_catalog"
    ),

    url(
        r"^(?P<view_type>[A-Za-z]+)/(?P<group_by>[A-Za-z]+)/$",
        CatalogView.as_view(
            model=PropertyPublication,
            catalog='properties',
            form_class=FilterForm
        ),
        name="property_catalog"
    ),

    url(
        r"^(?P<pk>\d+)/$",
        DetailView.as_view(model=PropertyPublication),
        name="detail"
    ),

    url(
        r"^test/(?P<pk>\d+)/$",
        DetailView.as_view(model=Test),
        name="test_detail"
    ),
)
