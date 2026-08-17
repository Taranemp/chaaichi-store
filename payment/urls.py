from django.urls import path

from .views import (
    GatewayPaymentStartView,
    GatewayPaymentCallbackView,
    PaymentSuccessView,
    PaymentFailedView,
)

app_name = "payment"


urlpatterns = [

    # =====================================================
    # START GATEWAY PAYMENT
    # =====================================================

    path(
        "gateway/start/<int:pk>/",
        GatewayPaymentStartView.as_view(),
        name="start_gateway",  # اصلاح نام جهت همخوانی با views.py
    ),

    # =====================================================
    # GATEWAY CALLBACK
    # =====================================================

    path(
        "verify/",
        GatewayPaymentCallbackView.as_view(),
        name="callback",  # نام استاندارد برای آدرس بازگشت درگاه
    ),

    # =====================================================
    # PAYMENT SUCCESS
    # =====================================================

    path(
        "success/<int:pk>/",
        PaymentSuccessView.as_view(),
        name="success",
    ),

    # =====================================================
    # PAYMENT FAILED
    # =====================================================

    path(
        "failed/<int:pk>/",
        PaymentFailedView.as_view(),
        name="failed",
    ),
]