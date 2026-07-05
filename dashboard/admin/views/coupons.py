# dashboard/admin/views/coupons.py
from typing import Any
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import FieldError
from django.utils import timezone

from dashboard.permissions import HasAdminAccessPermission
from order.models import Coupon
from dashboard.admin.forms import CouponForm


class AdminCouponListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/coupons/coupon-list.html"
    model = Coupon
    paginate_by = 10
    context_object_name = "coupons"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = Coupon.objects.all()
        
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(code__icontains=search_q)
        
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["active_coupons"] = self.get_queryset().filter(is_active=True).count()
        context["expired_coupons"] = self.get_queryset().filter(
            expiration_date__lt=timezone.now()
        ).count()
        
        context["current_search"] = self.request.GET.get("q", "")
        context["current_order_by"] = self.request.GET.get("order_by", "")
        context["current_page_size"] = self.request.GET.get("page_size", "10")
        
        return context


class AdminCouponCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/coupons/coupon-create.html"
    model = Coupon
    form_class = CouponForm
    success_message = "کد تخفیف با موفقیت ایجاد شد"

    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(reverse_lazy("dashboard:admin:coupon-edit", kwargs={"pk": form.instance.pk}))

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:coupon-list")


class AdminCouponEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/coupons/coupon-edit.html"
    model = Coupon
    form_class = CouponForm
    success_message = "کد تخفیف با موفقیت ویرایش شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:coupon-edit", kwargs={"pk": self.get_object().pk})


class AdminCouponDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/coupons/coupon-delete.html"
    model = Coupon
    success_url = reverse_lazy("dashboard:admin:coupon-list")
    success_message = "کد تخفیف با موفقیت حذف شد"