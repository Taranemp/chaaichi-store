# order/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, UserAddress, Coupon


class OrderItemInline(admin.TabularInline):
    """نمایش آیتم‌های سفارش در صفحه سفارش"""
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "subtotal_display")
    fields = ("product", "quantity", "price", "subtotal_display")
    
    def subtotal_display(self, obj):
        return f"{obj.price * obj.quantity:,} تومان"
    subtotal_display.short_description = "جمع"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """پنل مدیریت سفارشات"""
    
    list_display = (
        "id",
        "user_display",
        "total_price_display",
        "order_status",
        "payment_status_display",
        "item_count",
        "created_date_display",
    )
    
    list_filter = (
        "status",
        "transaction__status",
        "created_date",
        "coupon",
    )
    
    search_fields = (
        "id",
        "user__phone",
        "user__email",
        "user__profile__first_name",
        "user__profile__last_name",
        "address",
        "city",
    )
    
    readonly_fields = (
        "created_date",
        "updated_date",
        "transaction",
        "total_price",
        "coupon",
    )
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ("اطلاعات کاربر", {
            "fields": ("user",)
        }),
        ("اطلاعات پرداخت", {
            "fields": ("transaction", "coupon", "total_price")
        }),
        ("آدرس تحویل", {
            "fields": ("address", "state", "city", "zip_code")
        }),
        ("وضعیت", {
            "fields": ("status",)
        }),
        ("تاریخ", {
            "fields": ("created_date", "updated_date")
        }),
    )
    
    actions = ["mark_as_success", "mark_as_failed", "mark_as_pending"]
    
    # ========== متدهای نمایش ==========
    
    def user_display(self, obj):
        return obj.user.profile.get_fullname() or obj.user.phone
    user_display.short_description = "کاربر"
    user_display.admin_order_field = "user__phone"
    
    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"
    total_price_display.short_description = "مبلغ کل"
    
    def order_status(self, obj):
        status_colors = {
            1: "#ffc107",   # PENDING - زرد
            2: "#28a745",   # SUCCESS - سبز
            3: "#dc3545",   # FAILED - قرمز
        }
        color = status_colors.get(obj.status, "#6c757d")
        label = obj.get_status()['label']
        return format_html('<span style="color: {}; font-weight: 600;">{}</span>', color, label)
    order_status.short_description = "وضعیت سفارش"
    
    def payment_status_display(self, obj):
        if obj.transaction:
            status_colors = {
                1: "#ffc107",  # PENDING
                2: "#28a745",  # SUCCESS
                3: "#dc3545",  # FAILED
            }
            color = status_colors.get(obj.transaction.status, "#6c757d")
            label = obj.transaction.get_status_display()
            return format_html('<span style="color: {};">{}</span>', color, label)
        return "---"
    payment_status_display.short_description = "وضعیت پرداخت"
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "تعداد آیتم"
    
    def created_date_display(self, obj):
        return obj.created_date.strftime("%Y/%m/%d %H:%M")
    created_date_display.short_description = "تاریخ ثبت"
    
    # ========== اکشن‌ها ==========
    
    @admin.action(description="تغییر وضعیت به موفق")
    def mark_as_success(self, request, queryset):
        updated = queryset.update(status=OrderStatusType.SUCCESS.value)
        self.message_user(request, f"{updated} سفارش به وضعیت موفق تغییر یافت.")
    
    @admin.action(description="تغییر وضعیت به ناموفق")
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status=OrderStatusType.FAILED.value)
        self.message_user(request, f"{updated} سفارش به وضعیت ناموفق تغییر یافت.")
    
    @admin.action(description="تغییر وضعیت به در انتظار")
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status=OrderStatusType.PENDING.value)
        self.message_user(request, f"{updated} سفارش به وضعیت در انتظار تغییر یافت.")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """پنل مدیریت آیتم‌های سفارش"""
    
    list_display = (
        "id",
        "order_display",
        "product_display",
        "quantity",
        "price_display",
        "subtotal_display",
        "created_date",
    )
    
    list_filter = ("created_date",)
    search_fields = ("order__id", "product__title", "order__user__phone")
    readonly_fields = ("created_date", "updated_date")
    
    def order_display(self, obj):
        return f"#{obj.order.id}"
    order_display.short_description = "سفارش"
    order_display.admin_order_field = "order__id"
    
    def product_display(self, obj):
        return obj.product.title
    product_display.short_description = "محصول"
    product_display.admin_order_field = "product__title"
    
    def price_display(self, obj):
        return f"{obj.price:,} تومان"
    price_display.short_description = "قیمت واحد"
    
    def subtotal_display(self, obj):
        return f"{obj.price * obj.quantity:,} تومان"
    subtotal_display.short_description = "جمع"


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """پنل مدیریت آدرس‌های کاربران"""
    
    list_display = (
        "id",
        "user_display",
        "address",
        "city_display",
        "state_display",
        "is_default_display",
        "created_date",
    )
    
    list_filter = ("is_default", "city", "state", "created_date")
    search_fields = ("user__phone", "user__email", "address", "city", "state")
    readonly_fields = ("created_date", "updated_date")
    
    def user_display(self, obj):
        return obj.user.profile.get_fullname() or obj.user.phone
    user_display.short_description = "کاربر"
    user_display.admin_order_field = "user__phone"
    
    def city_display(self, obj):
        return obj.city or "---"
    city_display.short_description = "شهر"
    
    def state_display(self, obj):
        return obj.state or "---"
    state_display.short_description = "استان"
    
    def is_default_display(self, obj):
        return "✅" if obj.is_default else "❌"
    is_default_display.short_description = "پیش‌فرض"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """پنل مدیریت کدهای تخفیف"""
    
    list_display = (
        "id",
        "code",
        "discount_percent_display",
        "max_limit_usage",
        "used_by_count",
        "is_active_display",
        "expiration_date_display",
        "created_date",
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
    
    actions = ["activate_coupons", "deactivate_coupons"]
    
    def discount_percent_display(self, obj):
        return f"{obj.discount_percent}%"
    discount_percent_display.short_description = "درصد تخفیف"
    
    def used_by_count(self, obj):
        return obj.used_by.count()
    used_by_count.short_description = "تعداد استفاده"
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745;">✅ فعال</span>')
        return format_html('<span style="color: #dc3545;">❌ غیرفعال</span>')
    is_active_display.short_description = "وضعیت"
    
    def expiration_date_display(self, obj):
        if obj.expiration_date:
            return obj.expiration_date.strftime("%Y/%m/%d %H:%M")
        return "---"
    expiration_date_display.short_description = "تاریخ انقضا"
    
    @admin.action(description="فعال کردن کدهای تخفیف انتخاب شده")
    def activate_coupons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} کد تخفیف فعال شدند.")
    
    @admin.action(description="غیرفعال کردن کدهای تخفیف انتخاب شده")
    def deactivate_coupons(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} کد تخفیف غیرفعال شدند.")