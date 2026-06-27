from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core import exceptions

from dashboard.permissions import HasAdminAccessPermission
from account.models import UserType
from dashboard.admin.forms import UserForm

User = get_user_model()


class AdminUserListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    """لیست کاربران (فقط مشتریان عادی)"""
    template_name = "dashboard/admin/users/user-list.html"
    model = User
    paginate_by = 10
    context_object_name = "users"
    ordering = "-created_date"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        
        queryset = User.objects.filter(
            type=UserType.customer.value
        ).select_related('profile').order_by("-created_date")
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(profile__first_name__icontains=search_query) |
                Q(profile__last_name__icontains=search_query)
            )
        
        ordering_query = self.request.GET.get('ordering')
        if ordering_query:
            try:
                queryset = queryset.order_by(ordering_query)
            except exceptions.FieldError:
                pass
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["current_search"] = self.request.GET.get('q', '')
        context["current_ordering"] = self.request.GET.get('ordering', '')
        context["current_page_size"] = self.request.GET.get('page_size', '10')
        return context


class AdminUserUpdateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    """ویرایش کاربر"""
    template_name = "dashboard/admin/users/user-edit.html"
    model = User
    form_class = UserForm
    success_message = "کاربر با موفقیت ویرایش شد"

    def get_queryset(self):
        return User.objects.filter(type=UserType.customer.value)

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:user-edit", kwargs={"pk": self.get_object().pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_profile"] = self.get_object().profile
        return context


class AdminUserDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    """حذف کاربر"""
    template_name = "dashboard/admin/users/user-delete.html"
    model = User
    success_url = reverse_lazy("dashboard:admin:user-list")
    success_message = "کاربر با موفقیت حذف شد"

    def get_queryset(self):
        return User.objects.filter(type=UserType.customer.value)