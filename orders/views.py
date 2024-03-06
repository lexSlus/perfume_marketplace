from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderItem, Order
from orders.serializers import OrderItemSerializer, OrderSerializer, NonRegisteredUserOrderItemSerializer


class OrderItemAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        if request.user.is_authenticated:
            # Logic for registered users
            serializer = OrderItemSerializer(data=request.data, context={'request': request})
        else:
            # Logic for non-registered users
            serializer = NonRegisteredUserOrderItemSerializer(data=request.data)

        if serializer.is_valid():
            with transaction.atomic():
                order_item = serializer.save()
                # Create or get the order for the user
                order, created = Order.objects.get_or_create(user=order_item.user)
                order.items.add(order_item)
                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            order_item = OrderItem.objects.get(pk=pk)
        except OrderItem.DoesNotExist:
            return Response({'detail': 'Order item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_authenticated and request.user != order_item.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
