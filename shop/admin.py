from django.contrib import admin
from .models import (
    Category, 
    Brand, 
    Grade, 
    PackageType, 
    Product, 
    ProductImage,
    WishlistProductModel
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug", "created_date")
    prepopulated_fields = {"slug": ["title"]}
    search_fields = ["title"]
    list_filter = ["created_date"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_date")
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "level", "created_date" if hasattr(Grade, 'created_date') else "id")
    prepopulated_fields = {"slug": ["name"]}
    list_editable = ["level"]  


@admin.register(PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "weight_grams")
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    """نمایش تصاویر محصول در داخل صفحه محصول"""
    model = ProductImage
    extra = 1  # تعداد فیلدهای خالی برای آپلود تصویر جدید


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "title", 
        "brand", 
        "grade", 
        "package",
        "stock", 
        "status", 
        "price", 
        "get_final_price",
        "discount_percent", 
        "created_date"
    )
    
    list_filter = ["status", "brand", "grade", "package", "created_date"]
    
    search_fields = ["title", "description", "slug"]
    
    prepopulated_fields = {"slug": ["title"]}
    
    list_editable = ["stock", "status", "price", "discount_percent"]
    
    inlines = [ProductImageInline]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "slug", "category", "brand", "grade", "package")
        }),
        ("Description", {
            "fields": ("image", "description", "brief_description")
        }),
        ("Stock & Price", {
            "fields": ("stock", "price", "discount_percent", "status")
        }),
    )
    
    def get_final_price(self, obj):
        """نمایش قیمت پس از تخفیف"""
        return obj.get_price_with_comma()
    
    get_final_price.short_description = "Final Price"
    
    def save_model(self, request, obj, form, change):
       
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "file", "created_date")
    list_filter = ["created_date"]
    search_fields = ["product__title"]
    
    
    
@admin.register(WishlistProductModel)
class WishlistProductAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_date")
    list_filter = ("created_date",)
    search_fields = ("user__phone", "product__title")