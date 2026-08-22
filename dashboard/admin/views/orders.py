# dashboard/admin/views/orders.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import FieldError
from django.db.models import Q

from dashboard.permissions import HasAdminAccessPermission
from order.models import Order, OrderStatusType, OrderItem


class AdminOrderListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    """لیست سفارشات"""
    template_name = "dashboard/admin/orders/order-list.html"
    model = Order
    paginate_by = 10
    context_object_name = "orders"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        # اصلاح شد: transaction به payment تغییر یافت
        queryset = Order.objects.all().select_related('user', 'payment', 'coupon')
        
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(
                Q(id__icontains=search_q) |
                Q(user__phone__icontains=search_q)
            )
        
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
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
        return context


class AdminOrderDetailView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    """نمایش جزئیات سفارش"""
    template_name = "dashboard/admin/orders/order-detail.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        # اصلاح شد: transaction به payment تغییر یافت
        return Order.objects.all().select_related('user', 'payment', 'coupon')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context["order_items"] = order.items.select_related('product').all()
        context["status_types"] = OrderStatusType.choices
        return context


class AdminOrderInvoiceView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    """نمایش فاکتور سفارش"""
    template_name = "dashboard/admin/orders/order-invoice.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(status=OrderStatusType.SUCCESS.value)


class AdminOrderUpdateStatusView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DetailView):
    """تغییر وضعیت سفارش"""
    http_method_names = ['post']
    model = Order
    success_message = "وضعیت سفارش با موفقیت تغییر کرد"

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.POST.get('status')
        
        if new_status and int(new_status) in [choice[0] for choice in OrderStatusType.choices]:
            order.status = new_status
            order.save()
            messages.success(request, f"وضعیت سفارش #{order.id} تغییر کرد.")
        else:
            messages.error(request, "وضعیت انتخاب شده معتبر نیست.")
        
        return redirect('dashboard:admin:order-detail', pk=order.id)