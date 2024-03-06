from django.db import models

from accounts.models import Account
from perfumes.models import Offer


class OrderItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    # Додаткові поля для незареєстрованих користувачів
    non_registered_first_name = models.CharField(max_length=100, blank=True, null=True)
    non_registered_last_name = models.CharField(max_length=100, blank=True, null=True)
    non_registered_email = models.EmailField(blank=True, null=True)
    non_registered_phone_number = models.CharField(max_length=15, blank=True, null=True)

    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    delivery_method = models.CharField(max_length=100)
    delivery_branch = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.offer.perfume.name

    def order_item_price(self):
        price = int(self.quantity) * int(self.offer.price_per_ml)
        return str(price)


class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(OrderItem, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Order for {self.user.full_name()} on {self.created_at}"
        else:
            return f"Order on {self.created_at}"
