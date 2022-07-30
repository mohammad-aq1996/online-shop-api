from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()

router.register('collections', views.CollectionViewSet)
router.register('products', views.ProductViewSet)
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('carts', views.CartViewSet)

domains_router = routers.NestedSimpleRouter(router, 'carts', lookup='carts')

domains_router.register('items', views.CartItemViewSet, basename='carts-items')



urlpatterns = [
    path('', include(router.urls)),
    path('', include(domains_router.urls))
]