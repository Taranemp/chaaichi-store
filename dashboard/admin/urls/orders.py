# dashboard/admin/urls/orders.py
from django.urls import path
from ..views.orders import (
    AdminOrderListView,
    AdminOrderDetailView,
    AdminOrderInvoiceView,
    AdminOrderUpdateStatusView,
)

app_name = "orders"

urlpatterns = [
    path("orders/", AdminOrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", AdminOrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/invoice/", AdminOrderInvoiceView.as_view(), name="order-invoice"),
    path("orders/<int:pk>/update-status/", AdminOrderUpdateStatusView.as_view(), name="order-update-status"),
]