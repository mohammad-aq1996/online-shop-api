from decimal import Decimal
from django.db import transaction
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
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = models.Customer
        fields = ('id', 'phone', 'birth_date', 'membership', 'user_id')


class CreateCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ('id', 'user')
        read_only_fields = ('id','user', )

    def save(self):
        self.instance = models.Cart.objects.create(user=self.context['user'], **self.validated_data)
        return self.instance

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'title', 'unit_price')


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many=False, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')

    def calculate_total_price(self, cart_item: models.CartItem):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = models.CartItem
        fields = ('id', 'product', 'quantity', 'total_price')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField(method_name='calculate_total_price')

    def calculate_total_price(self, cart: models.Cart):
        return sum([item.product.unit_price * item.quantity for item in cart.items.all()])

    class Meta:
        model = models.Cart
        fields = ('id', 'user', 'items', 'total_price')


class UpdateCartItemSerializer(serializers.ModelSerializer):    
    class Meta:
        model = models.CartItem
        fields = ('quantity',)


class AddItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = models.CartItem
        fields = ('id', 'product_id', 'quantity')

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found.')
        return value

    def save(self):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = models.CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            cart_item.quantity += int(quantity)
            cart_item.save()
            self.instance = cart_item

        except:
            self.instance = models.CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not models.Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if models.CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            customer = models.Customer.objects.get(
                user_id=self.context['user_id'])
            order = models.Order.objects.create(customer=customer)

            cart_items = models.CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                models.OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            models.OrderItem.objects.bulk_create(order_items)
            models.Cart.objects.filter(pk=cart_id).delete()
            return order


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = models.OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = models.Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['payment_status']