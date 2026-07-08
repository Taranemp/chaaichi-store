from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, ProductStatusType, Category, Brand, Grade

from review.models import Review, ReviewStatusType


class ProductGridView(ListView):
    """
    صفحه لیست محصولات
    """
    template_name = "shop/product-grid.html"
    paginate_by = 5
    context_object_name = "object_list"

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = Product.objects.select_related(
            "brand",
            "grade"
        ).prefetch_related(
            "category"
        ).filter(
            status=ProductStatusType.PUBLISH.value
        )

        # Search
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(title__icontains=search_q) |
                Q(description__icontains=search_q) |
                Q(brief_description__icontains=search_q)
            )

        # Category filter
        if category_id := self.request.GET.get("category_id"):
            queryset = queryset.filter(category__id=category_id)

        # Brand filter
        if brand_id := self.request.GET.get("brand_id"):
            queryset = queryset.filter(brand__id=brand_id)

        # Grade filter
        if grade_id := self.request.GET.get("grade_id"):
            queryset = queryset.filter(grade__id=grade_id)

        # Min price
        try:
            if min_price := self.request.GET.get("min_price"):
                queryset = queryset.filter(price__gte=min_price)
        except ValueError:
            pass

        # Max price
        try:
            if max_price := self.request.GET.get("max_price"):
                queryset = queryset.filter(price__lte=max_price)
        except ValueError:
            pass

        # Ordering
        allowed_orders = [
            "created_date",
            "-created_date",
            "price",
            "-price",
        ]

        order_by = self.request.GET.get("order_by", "-created_date")

        if order_by in allowed_orders:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by("-created_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_items"] = self.object_list.count()

        # Filters
        context["categories"] = Category.objects.all()
        context["brands"] = Brand.objects.all()
        context["grades"] = Grade.objects.all()

        # Placeholder for future wishlist system
        context["wishlist_items"] = []

        return context


class ProductDetailView(DetailView):
    """
    صفحه جزئیات محصول
    """
    template_name = "shop/product-detail.html"
    model = Product
    context_object_name = "object"

    def get_queryset(self):
        return Product.objects.select_related(
            "brand",
            "grade"
        ).prefetch_related(
            "category"
        ).filter(
            status=ProductStatusType.PUBLISH.value
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # محصولات مرتبط (همان برند)
        context["related_products"] = Product.objects.filter(
            brand=product.brand,
            status=ProductStatusType.PUBLISH.value
        ).exclude(id=product.id)[:4]

        # دیدگاه‌های تایید‌شده
        context["reviews"] = Review.objects.filter(
            product=product,
            status=ReviewStatusType.APPROVED.value
        ).select_related("user", "user__profile")

        # برای رسم ستاره‌ی میانگین امتیاز به‌صورت گرد‌شده
        context["avg_rating_rounded"] = round(product.avg_rating)

        # بررسی اینکه کاربر لاگین‌شده قبلاً برای این محصول دیدگاه ثبت کرده یا نه
        context["user_has_reviewed"] = (
            self.request.user.is_authenticated
            and Review.objects.filter(user=self.request.user, product=product).exists()
        )

        return context