from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core.exceptions import FieldError

from dashboard.permissions import HasCustomerAccessPermission
from shop.models import WishlistProductModel


class CustomerWishlistListView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    template_name = "dashboard/customer/wishlists/wishlist-list.html"
    model = WishlistProductModel
    paginate_by = 12
    context_object_name = "wishlist_items"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = WishlistProductModel.objects.filter(
            user=self.request.user
        ).select_related('product')
        
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(product__title__icontains=search_q)
        
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
        return context


class CustomerWishlistDeleteView(LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, DeleteView):
    model = WishlistProductModel
    success_url = reverse_lazy('dashboard:customer:wishlist-list')
    success_message = "محصول با موفقیت از لیست علاقه‌مندی حذف شد"

    def get_queryset(self):
        return WishlistProductModel.objects.filter(user=self.request.user)