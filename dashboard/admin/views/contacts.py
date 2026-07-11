# dashboard/admin/views/contacts.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.exceptions import FieldError

from dashboard.permissions import HasAdminAccessPermission
from website.models import Contact


class AdminContactListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    """لیست پیام‌های تماس"""
    template_name = "dashboard/admin/contacts/contact-list.html"
    model = Contact
    paginate_by = 10
    context_object_name = "contacts"
    ordering = "-created_date"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = Contact.objects.all().order_by("-created_date")
        
        # جستجو
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(
                Q(full_name__icontains=search_q) |
                Q(email__icontains=search_q) |
                Q(subject__icontains=search_q) |
                Q(content__icontains=search_q) |
                Q(phone_number__icontains=search_q)
            )
        
        # فیلتر بر اساس وضعیت دیده شدن
        status = self.request.GET.get("status")
        if status == "seen":
            queryset = queryset.filter(is_seen=True)
        elif status == "unseen":
            queryset = queryset.filter(is_seen=False)
        
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
        context["unseen_count"] = Contact.objects.filter(is_seen=False).count()
        
        # حفظ مقادیر فیلتر
        context["current_search"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_order_by"] = self.request.GET.get("order_by", "")
        context["current_page_size"] = self.request.GET.get("page_size", "10")
        
        return context


class AdminContactDetailView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    """جزئیات پیام تماس"""
    template_name = "dashboard/admin/contacts/contact-detail.html"
    model = Contact
    context_object_name = "contact"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # اگر پیام دیده نشده بود، دیده شده علامت بزن
        if not obj.is_seen:
            obj.is_seen = True
            obj.save()
        return obj