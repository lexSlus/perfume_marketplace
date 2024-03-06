from django.urls import path

from orders.views import OrderItemAPIView, UserOrderAPIView

urlpatterns = [
    path('item/create/', OrderItemAPIView.as_view(), name='orderitem-create'),
    path('item/<int:pk>/delete/', OrderItemAPIView.as_view(), name='orderitem-delete'),
    path('', UserOrderAPIView.as_view(), name='user-order-list'),

]
