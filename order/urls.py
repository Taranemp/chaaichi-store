# order/urls.py
from django.urls import path
from . import views

app_name = "order"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("success/", views.OrderSuccessView.as_view(), name="success"),
    path("failed/", views.OrderFailedView.as_view(), name="failed"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
]