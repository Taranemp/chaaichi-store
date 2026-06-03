# order/admin.py
from django.contrib import admin
from .models import Order, OrderItem, Coupon, UserAddress


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_price",
        "transaction",
        "coupon",
        "status",
        "created_date"
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "created_date"
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_limit_usage",
        "used_by_count",
        "expiration_date",
        "created_date"
    )
    
    def used_by_count(self, obj):
        return obj.used_by.all().count()
    used_by_count.short_description = "Used By Count"


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "state",
        "city",
        "zip_code",
        "created_date"
    )