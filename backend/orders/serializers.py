from rest_framework import serializers
from .models import Order, OrderItem

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # Optionally, include a read-only representation for the related user
    requested_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

