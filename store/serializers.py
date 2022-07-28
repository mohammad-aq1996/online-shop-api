from decimal import Decimal
from rest_framework import serializers
from . import models


class CollectionSerialiers(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ('id', 'title')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'title', 'price_with_tax', 'description', 'unit_price', 'inventory', 'last_update', 'collection')
    
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product:models.Product):
        return product.unit_price * Decimal(1.1)
        

class CustomreSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    class Meta:
        model = models.Customer
        fields = ('id', 'phone', 'birth_date', 'membership', 'user_id')