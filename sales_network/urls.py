from .views import NetworkElementViewSet, ProductViewSet
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'network'

router.register(r'product', ProductViewSet, basename='product')
router.register(r'network', NetworkElementViewSet, basename='network')

urlpatterns = router.urls
