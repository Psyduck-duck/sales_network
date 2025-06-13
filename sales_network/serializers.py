from rest_framework import serializers

from .models import Product, NetworkElement


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class NetworkElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkElement
        fields = '__all__'
        read_only_fields = ('debt_to_parent',)
