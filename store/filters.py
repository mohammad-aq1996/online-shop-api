from itertools import product
from django_filters.rest_framework import FilterSet
from . import models


class ProductFilter(FilterSet):
    class Meta:
        model = models.Product
        fields = {
            'unit_price': ['gte', 'lte']
        }