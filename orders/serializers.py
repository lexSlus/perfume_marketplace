import random
import string

from django.db import transaction
from rest_framework import serializers

from accounts.models import Account, UserProfile
from accounts.serializers import AccountSerializer
from accounts.task import send_confirmation_email_task
from accounts.utils import send_confirmation_email
from orders.models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'user', 'offer', 'quantity', 'created_at', 'city', 'district', 'delivery_method',
                  'delivery_branch', 'order_item_price']

        extra_kwargs = {
            'user': {'required': False, 'allow_null': True}
        }


class OrderSerializer(serializers.ModelSerializer):
    user = AccountSerializer()  # Assuming you have an AccountSerializer
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


class NonRegisteredUserOrderItemSerializer(serializers.ModelSerializer):
    non_registered_first_name = serializers.CharField(required=True)
    non_registered_last_name = serializers.CharField(required=True)
    non_registered_email = serializers.EmailField(required=True)
    non_registered_phone_number = serializers.CharField(required=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'offer', 'quantity', 'created_at', 'city', 'district', 'delivery_method', 'delivery_branch',
                  'non_registered_first_name', 'non_registered_last_name', 'non_registered_email',
                  'non_registered_phone_number', 'order_item_price']

    def create(self, validated_data):
        with transaction.atomic():
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user, user_created = Account.objects.get_or_create(
                email=validated_data['non_registered_email'],
                defaults={
                    'first_name': validated_data['non_registered_first_name'],
                    'last_name': validated_data['non_registered_last_name'],
                    'phone_number': validated_data['non_registered_phone_number'],
                }
            )

            if user_created:
                user.set_password(password)
                user.generate_confirmation_token()
                user.save()
                UserProfile.objects.get_or_create(user=user)  # Use get_or_create to avoid duplicates
                send_confirmation_email_task.delay(user.email, user.confirmation_token, password)
                send_confirmation_email(user.email, user.confirmation_token, password)
                # Logic to send password to user's email

            order_item = OrderItem.objects.create(user=user, **validated_data)
            return order_item
