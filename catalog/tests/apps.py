#  require django >= 1.7
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CatalogTestsConfig(AppConfig):
    name = 'catalog.tests'
    verbose_name = _('Catalog Tests')
