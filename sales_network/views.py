from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, NetworkElement
from users.permissions import IsActiveUser
from .serializers import ProductSerializer, NetworkElementSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveUser, IsAuthenticated]


class NetworkElementViewSet(viewsets.ModelViewSet):
    queryset = NetworkElement.objects.all()
    serializer_class = NetworkElementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']
    permission_classes = [IsActiveUser, IsAuthenticated]
