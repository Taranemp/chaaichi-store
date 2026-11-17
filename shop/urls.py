from django.urls import path, register_converter
from .views import ProductGridView, ProductDetailView, toggle_wishlist


class UnicodeSlugConverter:
    # \w در پایتون ۳ حروف یونیکد (فارسی) رو هم شامل میشه
    regex = r"[-\w]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(UnicodeSlugConverter, "uslug")

app_name = "shop"

urlpatterns = [
    path(
        "products/",
        ProductGridView.as_view(),
        name="product_grid"
    ),
    path(
        "products/<uslug:slug>/",
        ProductDetailView.as_view(),
        name="product_detail"
    ),
    path(
        "toggle-wishlist/",
        toggle_wishlist,
        name="toggle-wishlist"
    ),
]