from django.contrib import admin

from .models import (
    Order,
    OrderItem,
    UserAddress,
    Coupon,
)


# =========================
# Order Item Inline
# =========================

class OrderItemInline(admin.TabularInline):

    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "product_title",
        "product_slug",
        "quantity",
        "original_price",
        "discount_amount",
        "unit_price",
        "subtotal_display",
    )

    fields = (
        "product",
        "product_title",
        "quantity",
        "original_price",
        "discount_amount",
        "unit_price",
        "subtotal_display",
    )


    def subtotal_display(self, obj):
        return f"{obj.subtotal:,} تومان"

    subtotal_display.short_description = "جمع نهایی"


# =========================
# Order Admin
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "total_price_display",
        "status_display",
        "created_date",
    )

    list_filter = (
        "status",
        "created_date",
    )

    search_fields = (
        "user__phone",
        "user__email",
        "id",
    )

    readonly_fields = (
        "items_total",
        "products_discount",
        "coupon_discount",
        "shipping_cost",
        "total_price",
        "created_date",
        "updated_date",
    )

    inlines = [
        OrderItemInline,
    ]


    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"

    total_price_display.short_description = "مبلغ نهایی"


    def status_display(self, obj):
        return obj.get_status()["label"]

    status_display.short_description = "وضعیت"


# =========================
# Order Item Admin
# =========================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "product_title",
        "quantity",
        "original_price_display",
        "discount_display",
        "unit_price_display",
        "subtotal_display",
    )

    search_fields = (
        "product_title",
        "product_slug",
    )


    readonly_fields = (
        "product",
        "product_title",
        "product_slug",
        "quantity",
        "original_price",
        "discount_amount",
        "unit_price",
    )


    def original_price_display(self, obj):
        return f"{obj.original_price:,} تومان"

    original_price_display.short_description = "قیمت اصلی"


    def discount_display(self, obj):
        return f"{obj.discount_amount:,} تومان"

    discount_display.short_description = "تخفیف"


    def unit_price_display(self, obj):
        return f"{obj.unit_price:,} تومان"

    unit_price_display.short_description = "قیمت نهایی"


    def subtotal_display(self, obj):
        return f"{obj.subtotal:,} تومان"

    subtotal_display.short_description = "جمع"


# =========================
# User Address Admin
# =========================

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):

    list_display = (
        "receiver_name",
        "receiver_phone",
        "city",
        "state",
        "user",
    )

    search_fields = (
        "receiver_name",
        "receiver_phone",
        "user__phone",
    )


# =========================
# Coupon Admin
# =========================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "discount_percent",
        "is_active",
        "expiration_date",
        "max_limit_usage",
        "created_date",
    )

    list_filter = (
        "is_active",
        "expiration_date",
        "created_date",
    )

    search_fields = (
        "code",
        "description",
    )

    readonly_fields = (
        "created_date",
        "updated_date",
    )

    filter_horizontal = (
        "used_by",
    )