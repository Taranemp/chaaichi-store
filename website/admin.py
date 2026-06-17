# website/admin.py
from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "phone_number",
        "subject",
        "is_seen",
        "created_date"
    )
    
    list_filter = ("is_seen", "created_date")
    
    search_fields = ("full_name", "email", "phone_number", "subject", "content")
    
    readonly_fields = ("created_date", "updated_date")
    
    list_editable = ("is_seen",)
    
    fieldsets = (
        ("User Information", {
            "fields": ("full_name", "email", "phone_number")
        }),
        ("Message", {
            "fields": ("subject", "content")
        }),
        ("Status", {
            "fields": ("is_seen",)
        }),
        ("Timestamps", {
            "fields": ("created_date", "updated_date")
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.save()
        else:
            obj.save()