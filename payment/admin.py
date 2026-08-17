from django.contrib import admin

from .models import (
    Payment,
    PaymentStatusType,
    PaymentMethodType,
    PaymentPurposeType,
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "amount_display",
        "method_display",
        "purpose_display",
        "status_display",
        "reference_id",
        "created_date",
    )

    list_display_links = (
        "id",
        "user",
    )

    list_filter = (
        "status",
        "method",
        "purpose",
        "created_date",
    )

    search_fields = (
        "user__phone",
        "user__email",
        "authority",
        "reference_id",
        "description",
    )

    readonly_fields = (
        "created_date",
        "updated_date",
    )

    ordering = (
        "-created_date",
    )

    date_hierarchy = "created_date"

    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات پرداخت",
            {
                "fields": (
                    "user",
                    "amount",
                    "method",
                    "purpose",
                    "status",
                )
            },
        ),
        (
            "اطلاعات درگاه",
            {
                "fields": (
                    "authority",
                    "reference_id",
                )
            },
        ),
        (
            "توضیحات",
            {
                "fields": (
                    "description",
                )
            },
        ),
        (
            "تاریخ‌ها",
            {
                "fields": (
                    "created_date",
                    "updated_date",
                )
            },
        ),
    )

    @admin.display(
        description="مبلغ"
    )
    def amount_display(self, obj):
        return f"{obj.amount:,} تومان"

    @admin.display(
        description="روش پرداخت"
    )
    def method_display(self, obj):
        return obj.get_method_display()

    @admin.display(
        description="نوع پرداخت"
    )
    def purpose_display(self, obj):
        return obj.get_purpose_display()

    @admin.display(
        description="وضعیت"
    )
    def status_display(self, obj):
        return obj.get_status()["label"]