# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from ..decorators import catalogue_enabled, catalogue_enabled_templates


class Property(models.Model):
    name = models.CharField(max_length=100)
    picture = models.ImageField(null=True, upload_to="media/")
    owner = models.ForeignKey(User)


class OperationType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name


@catalogue_enabled
class PropertyPublication(models.Model):
    property = models.ForeignKey(Property, related_name='publications')
    operation_type = models.ForeignKey(OperationType, related_name="publications_of_type")
    details = models.TextField(max_length=5000, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=10, choices=[(1, "PUBLIC"), (2, "PRIVATE")])
    created = models.DateField()
    modified = models.DateTimeField(auto_now_add=True)

    def comments_aggregation(self):
        pass


class Comment(models.Model):
    publication = models.ForeignKey(PropertyPublication, related_name='comments')
    rating = models.IntegerField()


@catalogue_enabled_templates({
    'grid': 'tests/grid.html'
})
class Test(models.Model):
    pass