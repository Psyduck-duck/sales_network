from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Product, NetworkElement
from .serializers import ProductSerializer, NetworkElementSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class NetworkElementViewSet(viewsets.ModelViewSet):
    queryset = NetworkElement.objects.all()
    serializer_class = NetworkElementSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        new_element = serializer.save()
        if new_element.parent:
            new_element.network_lvl = new_element.parent.network_lvl + 1
        else:
            new_element.network_lvl = 0
