# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from ..decorators import catalogue_enabled


class Property(models.Model):
    name = models.CharField(max_length=100)
    picture = models.ImageField(null=True, upload_to="media/")
    owner = models.ForeignKey(User)


class OperationType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)

@catalogue_enabled
class PropertyPublication(models.Model):
    property = models.ForeignKey(Property, related_name='publications')
    operation_type = models.ForeignKey(OperationType, related_name="publications_of_type")
    details = models.TextField(max_length=5000, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=10, choices=[(1, "PUBLIC"), (2, "PRIVATE")])