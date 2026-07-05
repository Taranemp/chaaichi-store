from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_limit_usage",
        "used_by_count",
        "is_active",
        "expiration_date",
        "created_date"
    )
    
    list_filter = ("is_active", "expiration_date", "created_date")
    search_fields = ("code",)
    readonly_fields = ("created_date", "updated_date")
    filter_horizontal = ("used_by",)
    
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("code", "discount_percent", "max_limit_usage", "expiration_date")
        }),
        ("تنظیمات", {
            "fields": ("is_active", "min_purchase_amount", "description")
        }),
        ("آمار", {
            "fields": ("used_by", "created_date", "updated_date")
        }),
    )
    
    def used_by_count(self, obj):
        return obj.used_by.count()
    used_by_count.short_description = "تعداد استفاده"