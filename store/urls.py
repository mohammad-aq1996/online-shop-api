from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()

router.register('collections', views.CollectionViewSet)
router.register('products', views.ProductViewSet)
router.register('customers', views.CustomerViewSet)

urlpatterns = [
    path('', include(router.urls))
]