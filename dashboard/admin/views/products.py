from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import FieldError
from django.db.models import Q

from dashboard.permissions import HasAdminAccessPermission
from shop.models import Product, Category, Brand, Grade, PackageType, ProductStatusType, ProductImage
from dashboard.admin.forms import ProductForm, ProductImageForm


class AdminProductListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    """لیست محصولات با قابلیت جستجو و فیلتر"""
    template_name = "dashboard/admin/products/product-list.html"
    model = Product
    paginate_by = 10
    context_object_name = "products"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # جستجو
        search_q = self.request.GET.get("q")
        if search_q:
            queryset = queryset.filter(
                Q(title__icontains=search_q) |
                Q(description__icontains=search_q) |
                Q(brief_description__icontains=search_q)
            )
        
        # فیلتر دسته‌بندی
        category_id = self.request.GET.get("category_id")
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        
        # فیلتر برند
        brand_id = self.request.GET.get("brand_id")
        if brand_id:
            queryset = queryset.filter(brand__id=brand_id)
        
        # فیلتر قیمت
        min_price = self.request.GET.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.GET.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # فیلتر وضعیت
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
        context["categories"] = Category.objects.all()
        context["brands"] = Brand.objects.all()
        context["grades"] = Grade.objects.all()
        context["packages"] = PackageType.objects.all()
        context["status_types"] = ProductStatusType.choices
        
        # حفظ مقادیر فیلتر
        context["current_search"] = self.request.GET.get("q", "")
        context["current_category_id"] = self.request.GET.get("category_id", "")
        context["current_brand_id"] = self.request.GET.get("brand_id", "")
        context["current_min_price"] = self.request.GET.get("min_price", "")
        context["current_max_price"] = self.request.GET.get("max_price", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_order_by"] = self.request.GET.get("order_by", "")
        context["current_page_size"] = self.request.GET.get("page_size", "10")
        
        return context


class AdminProductCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    """ایجاد محصول جدید"""
    template_name = "dashboard/admin/products/product-create.html"
    model = Product
    form_class = ProductForm
    success_message = "محصول با موفقیت ایجاد شد"

    def form_valid(self, form):
        super().form_valid(form)
        return redirect(reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": form.instance.pk}))

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-list")


class AdminProductEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    """ویرایش محصول"""
    template_name = "dashboard/admin/products/product-edit.html"
    model = Product
    form_class = ProductForm
    success_message = "محصول با موفقیت ویرایش شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": self.get_object().pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = ProductImageForm()
        context["product_images"] = self.get_object().images.all()
        return context


class AdminProductDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    """حذف محصول"""
    template_name = "dashboard/admin/products/product-delete.html"
    model = Product
    success_url = reverse_lazy("dashboard:admin:product-list")
    success_message = "محصول با موفقیت حذف شد"


class AdminProductAddImageView(LoginRequiredMixin, HasAdminAccessPermission, CreateView):
    """افزودن تصویر به محصول"""
    http_method_names = ['post']
    form_class = ProductImageForm

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        form.instance.product = product
        messages.success(self.request, 'تصویر با موفقیت اضافه شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'خطا در افزودن تصویر')
        return redirect(reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')}))


class AdminProductRemoveImageView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    """حذف تصویر محصول"""
    http_method_names = ["post"]
    model = ProductImage
    success_message = "تصویر با موفقیت حذف شد"

    def get_queryset(self):
        return ProductImage.objects.filter(product__id=self.kwargs.get('pk'))

    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs.get('image_id'))

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:product-edit', kwargs={'pk': self.kwargs.get('pk')})