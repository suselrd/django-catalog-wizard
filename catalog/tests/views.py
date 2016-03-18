# coding=utf-8
from django.utils.datastructures import MultiValueDict
from catalog.decorators import log_search
from catalog.views import CatalogView
from .models import PropertyPublication
from .forms import FilterForm


@log_search
class PropertySalesCatalogView(CatalogView):
    model = PropertyPublication
    catalog = 'properties'
    form_class = FilterForm

    def get_fixed_filters(self):
        filters = MultiValueDict()
        filters['operation_type'] = '1'
        return filters
