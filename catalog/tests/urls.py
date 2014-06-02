# coding=utf-8
from django.conf.urls import patterns, url
from django.views.generic import DetailView
from .models import PropertyPublication
from ..views import CatalogView


urlpatterns = patterns(
    "",
    url(r"(?P<view_type>[A-Za-z]+)/(?P<group_by>[A-Za-z]+)/", CatalogView.as_view(model=PropertyPublication, catalog='properties'), name="property_catalog"),
    url(r"(?P<pk>\d+)", DetailView.as_view(model=PropertyPublication), name="detail"),
)


