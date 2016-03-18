# coding=utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


MODEL_CONTEXT_TEMPLATES_CACHE = {}


class ModelContextTemplateManager(models.Manager):

    def get_by_natural_key(self, model, context):
        if (
            model in MODEL_CONTEXT_TEMPLATES_CACHE and
            MODEL_CONTEXT_TEMPLATES_CACHE.get(model).get(context, None) and
            not isinstance(MODEL_CONTEXT_TEMPLATES_CACHE.get(model).get(context), self.model)
        ):
            template = MODEL_CONTEXT_TEMPLATES_CACHE[model][context]
            try:
                MODEL_CONTEXT_TEMPLATES_CACHE[model][context] = self.get(model=model, context=context)
            except self.model.DoesNotExist:
                MODEL_CONTEXT_TEMPLATES_CACHE[model][context] = self.model(model=model, context=context)
            MODEL_CONTEXT_TEMPLATES_CACHE[model][context].template = template
            MODEL_CONTEXT_TEMPLATES_CACHE[model][context].save()

        return MODEL_CONTEXT_TEMPLATES_CACHE.get(model, {}).get(context, None)


@python_2_unicode_compatible
class ModelContextTemplate(models.Model):
    model = models.CharField(_(u'Model'), max_length=200)
    context = models.CharField(_(u'Context'), max_length=20)
    template = models.CharField(_(u'Template'), max_length=100)

    objects = ModelContextTemplateManager()

    class Meta(object):
        verbose_name = _(u'Model Context Template')
        verbose_name_plural = _(u'Model Context Templates')
        unique_together = ('model', 'context')

    def __str__(self):
        return u"%s-%s" % self.model, self.context

    def natural_key(self):
        return self.model, self.context


@python_2_unicode_compatible
class SearchLog(models.Model):
    model = models.CharField(max_length=200, verbose_name=_('Model'))
    querystring = models.TextField(verbose_name=_('QueryString'))

    class Meta(object):
        verbose_name = _(u'Search Log')
        verbose_name_plural = _(u'Search Logs')

    def __str__(self):
        return u"%s-%s" % self.model, self.querystring
