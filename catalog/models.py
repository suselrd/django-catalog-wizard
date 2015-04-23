# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ModelContextTemplate(models.Model):
    model = models.CharField(max_length=200, verbose_name=_('Model'))
    context = models.CharField(max_length=20, verbose_name=_('Context'))
    template = models.CharField(max_length=100, verbose_name=_('Template'))

    class Meta:
        verbose_name = _('Model Context Template')
        verbose_name_plural = _('Model Context Templates')
        unique_together = ('model', 'context')


class SearchLog(models.Model):
    model = models.CharField(max_length=200, verbose_name=_('Model'))
    querystring = models.TextField(verbose_name=_('QueryString'))

    class Meta:
        verbose_name = _('Search Log')
        verbose_name_plural = _('Search Logs')