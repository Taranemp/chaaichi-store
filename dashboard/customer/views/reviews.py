from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import FieldError
from django.db.models import Q

from dashboard.permissions import HasCustomerAccessPermission
from review.models import Review, ReviewStatusType


class CustomerReviewListView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    """لیست نظرات کاربر"""
    template_name = "dashboard/customer/reviews/reviews-list.html"
    model = Review
    paginate_by = 10
    context_object_name = "reviews"
    ordering = "-created_date"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        # فقط نظرات کاربر فعلی
        queryset = Review.objects.filter(
            user=self.request.user
        ).select_related('product', 'product__brand').order_by("-created_date")
        
        # جستجو در عنوان محصول
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(
                Q(product__title__icontains=search_q) |
                Q(comment__icontains=search_q)
            )
        
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
        context["status_types"] = ReviewStatusType.choices
        
        # آمار نظرات
        queryset = self.get_queryset()
        context["pending_count"] = queryset.filter(status=ReviewStatusType.PENDING.value).count()
        context["approved_count"] = queryset.filter(status=ReviewStatusType.APPROVED.value).count()
        context["rejected_count"] = queryset.filter(status=ReviewStatusType.REJECTED.value).count()
        
        # حفظ مقادیر فیلتر
        context["current_search"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_order_by"] = self.request.GET.get("order_by", "")
        context["current_page_size"] = self.request.GET.get("page_size", "10")
        
        return context