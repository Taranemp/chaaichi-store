# dashboard/admin/views/profiles.py
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from dashboard.permissions import HasAdminAccessPermission
from account.models import Profile
from dashboard.admin.forms import AdminPasswordChangeForm, AdminProfileEditForm


class AdminSecurityEditView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    auth_views.PasswordChangeView
):
    """تغییر رمز عبور ادمین"""
    template_name = "dashboard/admin/profile/security-edit.html"
    form_class = AdminPasswordChangeForm
    success_url = reverse_lazy("dashboard:admin:security-edit")
    success_message = "رمز عبور با موفقیت تغییر کرد"


class AdminProfileEditView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView
):
    """ویرایش پروفایل ادمین"""
    template_name = "dashboard/admin/profile/profile-edit.html"
    form_class = AdminProfileEditForm
    success_url = reverse_lazy("dashboard:admin:profile-edit")
    success_message = "پروفایل با موفقیت ویرایش شد"

    def get_object(self, queryset=None):
        """دریافت پروفایل کاربر فعلی"""
        return Profile.objects.get(user=self.request.user)


class AdminProfileImageEditView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView
):
    """تغییر تصویر پروفایل ادمین"""
    http_method_names = ["post"]
    model = Profile
    fields = ["image"]
    success_url = reverse_lazy("dashboard:admin:profile-edit")
    success_message = "تصویر پروفایل با موفقیت به‌روزرسانی شد"

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    def form_invalid(self, form):
        messages.error(self.request, "ارسال تصویر با مشکل مواجه شده است. لطفاً مجدد تلاش نمایید.")
        return redirect(self.success_url)