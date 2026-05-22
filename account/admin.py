from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser


class UserCreationForm(forms.ModelForm):
    """Form to create user"""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["fullname", "phone", "email"]

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Form to update user"""

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ["fullname", "phone", "email", "password", "is_active", "is_staff", "is_superuser"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["id", "fullname", "phone", "email", "is_active", "is_staff", "is_superuser"]
    list_filter = ["is_active", "is_staff", "is_superuser"]

    fieldsets = [
        (None, {"fields": ["phone", "email", "password"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
    ]

    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": ["phone", "email", "password1", "password2"],
        }),
    ]

    search_fields = ["fullname", "phone", "email"]
    ordering = ["id"]
    filter_horizontal = ["groups", "user_permissions"]


    actions = ["activate_users", "deactivate_users"]


    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated_count = queryset.update(is_active=True)
        self.message_user(request, f"{updated_count} users successfully activated.")

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f"{updated_count} Users successfully deactivated.")


admin.site.register(CustomUser, UserAdmin)