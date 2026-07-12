from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from dashboard.permissions import HasCustomerAccessPermission
from account.models import Profile
from dashboard.customer.forms import CustomerPasswordChangeForm, CustomerProfileEditForm


class CustomerSecurityEditView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    SuccessMessageMixin,
    auth_views.PasswordChangeView
):
    """تغییر رمز عبور مشتری"""
    template_name = "dashboard/customer/profile/security-edit.html"
    form_class = CustomerPasswordChangeForm
    success_url = reverse_lazy("dashboard:customer:security-edit")
    success_message = "رمز عبور با موفقیت تغییر کرد"


class CustomerProfileEditView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    SuccessMessageMixin,
    UpdateView
):
    """ویرایش پروفایل مشتری"""
    template_name = "dashboard/customer/profile/profile-edit.html"
    form_class = CustomerProfileEditForm
    success_url = reverse_lazy("dashboard:customer:profile-edit")
    success_message = "پروفایل با موفقیت ویرایش شد"

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)


class CustomerProfileImageEditView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    SuccessMessageMixin,
    UpdateView
):
    """تغییر تصویر پروفایل مشتری"""
    http_method_names = ["post"]
    model = Profile
    fields = ["image"]
    success_url = reverse_lazy("dashboard:customer:profile-edit")
    success_message = "تصویر پروفایل با موفقیت به‌روزرسانی شد"

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    def form_invalid(self, form):
        messages.error(self.request, "ارسال تصویر با مشکل مواجه شده است. لطفاً مجدد تلاش نمایید.")
        return redirect(self.success_url)