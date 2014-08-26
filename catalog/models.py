# coding=utf-8
from django.db import models


class ModelContextTemplate(models.Model):
    model = models.CharField(max_length=200)
    context = models.CharField(max_length=20)
    template = models.CharField(max_length=100)

    class Meta:
        unique_together = ('model', 'context')


class SearchLog(models.Model):
    model = models.CharField(max_length=200)
    querystring = models.TextField()