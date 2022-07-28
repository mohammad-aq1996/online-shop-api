from rest_framework.viewsets import ModelViewSet
from . import models, serializers


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionSerialiers


class ProductViewSet(ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class CustomerViewSet(ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomreSerializer