from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from store.filters import ProductFilter
from . import models, serializers
from .permissions import IsSuperUserOrReadOnly


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionSerialiers


class ProductViewSet(ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']


class CustomerViewSet(ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomreSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = models.Customer.objects.get(user=request.user)
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            models.Cart.objects.all()
        return models.Cart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateCartSerializer
        return serializers.CartSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}


class CartItemViewSet(ModelViewSet):
    http_method_names = ('post', 'get', 'delete', 'patch')
    queryset = models.CartItem.objects.all()
    permission_classes = [IsAuthenticated]

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


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateOrderSerializer
        return serializers.OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return models.Order.objects.all()

        customer_id = models.Customer.objects.only(
            'id').get(user_id=user.id)
        return models.Order.objects.filter(customer_id=customer_id)