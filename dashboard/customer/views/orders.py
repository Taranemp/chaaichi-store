# dashboard/customer/views/orders.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.exceptions import FieldError

from dashboard.permissions import HasCustomerAccessPermission
from order.models import Order, OrderStatusType


class CustomerOrderListView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    """لیست سفارشات کاربر"""
    template_name = "dashboard/customer/orders/order-list.html"
    model = Order
    paginate_by = 10
    context_object_name = "orders"
    ordering = "-created_date"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
    # اضافه کردن prefetch_related برای بارگذاری سریع‌تر تصاویر اقلام در لیست
        queryset = Order.objects.filter(
            user=self.request.user
        ).select_related('user', 'transaction', 'coupon').prefetch_related('items__product').order_by("-created_date")
        
    # مابقی کدهای فیلتر شما بدون تغییر...
        
        # جستجو بر اساس شناسه سفارش
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(id__icontains=search_q)
        
        # فیلتر بر اساس وضعیت
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
        # مرتب‌سازی
        order_by = self.request.GET.get("order_by")
        if order_by:
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["status_types"] = OrderStatusType.choices
        
        # آمار سفارشات
        queryset = self.get_queryset()
        context["pending_count"] = queryset.filter(status=OrderStatusType.PENDING.value).count()
        context["success_count"] = queryset.filter(status=OrderStatusType.SUCCESS.value).count()
        context["failed_count"] = queryset.filter(status=OrderStatusType.FAILED.value).count()
        
        # حفظ مقادیر فیلتر
        context["current_search"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_order_by"] = self.request.GET.get("order_by", "")
        context["current_page_size"] = self.request.GET.get("page_size", "10")
        
        return context


class CustomerOrderDetailView(LoginRequiredMixin, HasCustomerAccessPermission, DetailView):
    """جزئیات سفارش کاربر"""
    template_name = "dashboard/customer/orders/order-detail.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        # فقط سفارشات کاربر فعلی
        return Order.objects.filter(user=self.request.user).select_related(
            'user', 'transaction', 'coupon'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context["order_items"] = order.items.select_related('product').all()
        context["status_types"] = OrderStatusType.choices
        return context