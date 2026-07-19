from django.urls import path
from ..views.orders import CustomerOrderListView, CustomerOrderDetailView

app_name = "orders"

urlpatterns = [
    path("orders/", CustomerOrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", CustomerOrderDetailView.as_view(), name="order-detail"),
]