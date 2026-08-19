from django.urls import path, include

app_name = "admin"

urlpatterns = [
    # برنامه‌های اصلی قبلی پروژه بدون پیشوند اضافه
    path("", include("dashboard.admin.urls.generals")),
    path("", include("dashboard.admin.urls.products")),
    path("", include("dashboard.admin.urls.orders")),
    path("", include("dashboard.admin.urls.users")),
    path("", include("dashboard.admin.urls.profiles")),
    path("", include("dashboard.admin.urls.coupons")),
    path("", include("dashboard.admin.urls.reviews")),
    path("", include("dashboard.admin.urls.contacts")),
    
    # فقط برای دسته‌بندی و برند پیشوند اختصاصی قرار می‌دهیم
    path("categories/", include("dashboard.admin.urls.categories")),
    path("brands/", include("dashboard.admin.urls.brands")),
    path("attributes/", include("dashboard.admin.urls.attributes")),
]