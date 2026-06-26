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
        fields = ("phone", "email")

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
        fields = ("phone", "email", "password", "is_active", "is_staff", "is_superuser", "is_verified", "type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'password':
                self.fields[field].widget.attrs['class'] = 'form-control'


# ========== پنل ادمین ==========

class ProfileInline(admin.StackedInline):
    """نمایش پروفایل در صفحه کاربر"""
    model = Profile
    can_delete = False
    verbose_name_plural = _("Profile")
    fields = ("first_name", "last_name", "phone_number", "image")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """پنل مدیریت کاربران"""
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = (
        "id",
        "phone",
        "email",
        "get_fullname",
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
        "type",
        "created_date"
    )
    
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_verified",
        "type",
        "created_date"
    )
    
    search_fields = ("phone", "email", "profile__first_name", "profile__last_name")
    ordering = ("-created_date",)
    
    fieldsets = (
        (None, {
            "fields": ("phone", "email", "password")
        }),
        (_("Profile"), {
            "fields": ("get_fullname",)
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_verified",
                "is_staff",
                "is_superuser",
                "type",
                "groups",
                "user_permissions"
            )
        }),
        (_("Important dates"), {
            "fields": ("last_login", "created_date", "updated_date")
        }),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "email", "password1", "password2"),
        }),
    )
    
    filter_horizontal = ("groups", "user_permissions")
    
    # ========== متدهای سفارشی ==========
    
    def get_fullname(self, obj):
        """نمایش نام کامل کاربر"""
        return obj.get_fullname()
    get_fullname.short_description = _("Full Name")
    get_fullname.admin_order_field = "profile__first_name"
    
    def get_phone_number(self, obj):
        """نمایش شماره تلفن پروفایل"""
        if hasattr(obj, 'profile') and obj.profile.phone_number:
            return obj.profile.phone_number
        return "-"
    get_phone_number.short_description = _("Profile Phone")
    
    # ========== اکشن‌ها ==========
    
    @admin.action(description=_("Activate selected users"))
    def activate_users(self, request, queryset):
        """فعال کردن کاربران انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} users activated.")
    
    @admin.action(description=_("Deactivate selected users"))
    def deactivate_users(self, request, queryset):
        """غیرفعال کردن کاربران انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} users deactivated.")
    
    @admin.action(description=_("Verify selected users"))
    def verify_users(self, request, queryset):
        """تأیید کاربران انتخاب شده"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} users verified.")
    
    actions = ["activate_users", "deactivate_users", "verify_users"]
    
    # ========== اضافه کردن Inline ==========
    
    inlines = [ProfileInline]


# ========== ثبت مدل Profile در ادمین ==========

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """پنل مدیریت پروفایل‌ها"""
    list_display = (
    "id",
    "user",
    "first_name",
    "last_name",
    "get_fullname",
    "created_date"
)
    list_filter = ("created_date", "updated_date")
    search_fields = ("user__phone", "first_name", "last_name", "phone_number")
    readonly_fields = ("created_date", "updated_date")
    
    fieldsets = (
        (None, {
            "fields": ("user", "first_name", "last_name", "phone_number", "image")
        }),
        (_("Timestamps"), {
            "fields": ("created_date", "updated_date")
        }),
    )