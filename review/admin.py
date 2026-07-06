# review/admin.py
from django.contrib import admin
from .models import Review, ReviewStatusType


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "rate",
        "status",
        "is_purchased",
        "created_date"
    )
    list_filter = ("status", "rate", "is_purchased", "created_date")
    search_fields = ("user__phone", "user__email", "product__title", "comment")
    readonly_fields = ("created_date", "updated_date")
    list_editable = ("status",)
    
    fieldsets = (
        ("Main Info", {
            "fields": ("user", "product", "comment", "rate")
        }),
        ("Status", {
            "fields": ("status", "is_purchased")
        }),
        ("Timestamps", {
            "fields": ("created_date", "updated_date")
        }),
    )
    
    actions = ["approve_reviews", "reject_reviews"]
    
    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(status=ReviewStatusType.APPROVED.value)
        self.message_user(request, f"{updated} reviews approved.")
    
    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        updated = queryset.update(status=ReviewStatusType.REJECTED.value)
        self.message_user(request, f"{updated} reviews rejected.")