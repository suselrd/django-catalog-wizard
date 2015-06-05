# coding=utf-8
from django.db.models.signals import post_syncdb
from . import models as catalog_app


def create_model_context_templates(sender, *args, **kwargs):
    from . import MODEL_CONTEXT_TEMPLATES
    for model, templates in MODEL_CONTEXT_TEMPLATES.items():
        for view_type, template in templates.items():
            sender.ModelContextTemplate.objects.get_or_create(
                model=model,
                context=view_type,
                defaults={
                    'template': template
                }
            )


post_syncdb.connect(create_model_context_templates, sender=catalog_app)
