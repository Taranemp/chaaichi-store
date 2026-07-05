from django.urls import path
from ..views.coupons import (
    AdminCouponListView,
    AdminCouponCreateView,
    AdminCouponEditView,
    AdminCouponDeleteView,
)

app_name = "coupons"

urlpatterns = [
    path("coupon/list/", AdminCouponListView.as_view(), name="coupon-list"),
    path("coupon/create/", AdminCouponCreateView.as_view(), name="coupon-create"),
    path("coupon/<int:pk>/edit/", AdminCouponEditView.as_view(), name="coupon-edit"),
    path("coupon/<int:pk>/delete/", AdminCouponDeleteView.as_view(), name="coupon-delete"),
]