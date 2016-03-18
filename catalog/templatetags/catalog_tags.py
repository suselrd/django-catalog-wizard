# coding=utf-8
from django import template
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.assignment_tag
def object_template(obj, tpl_context):
    """
    Gets the proper template to render an object in a given context

    Syntax::

         {% object_template [obj] [tpl_context] as [name] %}
    """
    from django.db.models import Model
    if not isinstance(obj, Model):
        raise Exception(_("The object must be a model instance"))

    return force_text(
        obj.__class__.get_object_template(tpl_context)
        if hasattr(obj.__class__, 'get_object_template')
        else "catalog/no_template.html"
    )
