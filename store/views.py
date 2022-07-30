from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from store.filters import ProductFilter
from . import models, serializers


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionSerialiers


class ProductViewSet(ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']


class CustomerViewSet(ModelViewSet):
    serializer_class = serializers.CustomreSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Customer.objects.all()
        return models.Customer.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        (customer, created) = models.Customer.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = serializers.CustomreSerializer(customer)
            return Response(serializer.data)
        else:
            serializer = serializers.CustomreSerializer(instance=customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class CartViewSet(ModelViewSet):
    http_method_names = ('post','get', 'delete', )
    queryset = models.Cart.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateCartSerializer
        return serializers.CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ('post', 'get', 'delete', 'patch')
    queryset = models.CartItem.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        else:
            return serializers.CartItemSerializer
            
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['carts_pk']}

    def get_queryset(self):
        return models.CartItem.objects.filter(cart_id=self.kwargs['carts_pk']).select_related('product')



