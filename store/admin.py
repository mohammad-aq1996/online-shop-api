from django.contrib import admin
from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update']
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title']



@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['featured_product']
    list_display = ['title']
    search_fields = ['title']


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['membership']
    list_per_page = 10
    list_select_related = ['user']
