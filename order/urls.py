from django.urls import path
from . import views

app_name = "order"

urlpatterns = [
    # صفحه نهایی‌سازی و ثبت سفارش
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),

    # صفحات نتیجه سفارش (همراه با دریافت آی‌دی سفارش)
    path("success/<int:pk>/", views.OrderSuccessView.as_view(), name="success"),
    path("failed/<int:pk>/", views.OrderFailedView.as_view(), name="failed"),

    # جزئیات سفارش در پنل کاربر
    path("detail/<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
]