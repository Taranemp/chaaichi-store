# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, UserType


class UserCreationForm(forms.ModelForm):
    """فرم ایجاد کاربر جدید در ادمین"""
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ("phone", "email", "type")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("Passwords do not match"))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """فرم ویرایش کاربر در ادمین"""
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        )
    )

    class Meta:
        model = User
        fields = ("phone", "email", "type", "is_active", "is_staff", "is_superuser")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'password':
                self.fields[field].widget.attrs['class'] = 'form-control'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """پنل مدیریت کاربران (ساده)"""
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = (
        "id",
        "phone",
        "email",
        "get_fullname",
        "type",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    
    list_filter = ("type", "is_active", "is_staff", "is_superuser")
    search_fields = ("phone", "email", "profile__first_name", "profile__last_name")
    ordering = ("-id",)
    
    fieldsets = (
        (None, {
            "fields": ("phone", "email", "password")
        }),
        ("User Type", {
            "fields": ("type",)
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser")
        }),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "email", "type", "password1", "password2"),
        }),
    )
    
    # حذف گروه‌ها و دسترسی‌ها
    filter_horizontal = ()
    
    def get_fullname(self, obj):
        return obj.get_fullname()
    get_fullname.short_description = _("Full Name")
    get_fullname.admin_order_field = "profile__first_name"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """پنل مدیریت پروفایل‌ها (ساده)"""
    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "get_fullname",
    )
    search_fields = ("user__phone", "first_name", "last_name")
    
    def get_fullname(self, obj):
        return obj.get_fullname()
    get_fullname.short_description = _("Full Name")