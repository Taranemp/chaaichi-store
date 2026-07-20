from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, ProductStatusType, Category, Brand, Grade, WishlistProductModel
from review.models import Review, ReviewStatusType


class ProductGridView(ListView):
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

        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(title__icontains=search_q) |
                Q(description__icontains=search_q) |
                Q(brief_description__icontains=search_q)
            )

        if category_id := self.request.GET.get("category_id"):
            queryset = queryset.filter(category__id=category_id)

        if brand_id := self.request.GET.get("brand_id"):
            queryset = queryset.filter(brand__id=brand_id)

        if grade_id := self.request.GET.get("grade_id"):
            queryset = queryset.filter(grade__id=grade_id)

        try:
            if min_price := self.request.GET.get("min_price"):
                queryset = queryset.filter(price__gte=min_price)
        except ValueError:
            pass

        try:
            if max_price := self.request.GET.get("max_price"):
                queryset = queryset.filter(price__lte=max_price)
        except ValueError:
            pass

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
        context["categories"] = Category.objects.all()
        context["brands"] = Brand.objects.all()
        context["grades"] = Grade.objects.all()

        # لیست محصولات علاقه‌مندی کاربر
        if self.request.user.is_authenticated:
            wishlist_ids = WishlistProductModel.objects.filter(
                user=self.request.user
            ).values_list('product_id', flat=True)
            context["wishlist_ids"] = list(wishlist_ids)
        else:
            context["wishlist_ids"] = []

        return context


class ProductDetailView(DetailView):
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

        # وضعیت علاقه‌مندی
        if self.request.user.is_authenticated:
            context["is_wished"] = WishlistProductModel.objects.filter(
                user=self.request.user,
                product=product
            ).exists()
        else:
            context["is_wished"] = False

        context["related_products"] = Product.objects.filter(
            brand=product.brand,
            status=ProductStatusType.PUBLISH.value
        ).exclude(id=product.id)[:4]

        reviews_qs = Review.objects.filter(
            product=product,
            status=ReviewStatusType.APPROVED.value
        ).select_related("user", "user__profile")

        review_order = self.request.GET.get("review_order", "newest")
        review_order_map = {
            "newest": "-created_date",
            "oldest": "created_date",
            "rating_high": "-rate",
            "rating_low": "rate",
        }
        reviews_qs = reviews_qs.order_by(review_order_map.get(review_order, "-created_date"))
        context["reviews"] = reviews_qs
        context["current_review_order"] = review_order

        review_stats = reviews_qs.aggregate(avg=Avg("rate"))
        context["live_avg_rating"] = round(review_stats["avg"], 1) if review_stats["avg"] else 0
        context["live_reviews_count"] = reviews_qs.count()
        context["avg_rating_rounded"] = round(review_stats["avg"]) if review_stats["avg"] else 0

        return context


@login_required
def toggle_wishlist(request):
    """افزودن یا حذف محصول از لیست علاقه‌مندی (AJAX)"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    product_id = request.POST.get("product_id")
    if not product_id:
        return JsonResponse({"error": "Product ID is required"}, status=400)

    product = get_object_or_404(Product, id=product_id)

    wishlist_item = WishlistProductModel.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        is_wished = False
        message = "محصول از لیست علاقه‌مندی حذف شد"
    else:
        WishlistProductModel.objects.create(
            user=request.user,
            product=product
        )
        is_wished = True
        message = "محصول به لیست علاقه‌مندی اضافه شد"

    total_wishlist = WishlistProductModel.objects.filter(user=request.user).count()

    return JsonResponse({
        "success": True,
        "is_wished": is_wished,
        "message": message,
        "total_wishlist": total_wishlist
    })