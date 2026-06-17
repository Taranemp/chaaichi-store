from django.urls import path
from .views import ProductGridView, ProductDetailView

app_name = "shop"

urlpatterns = [
    path(
        "products/",
        ProductGridView.as_view(),
        name="product_grid"
    ),

    path(
        "products/<slug:slug>/",
        ProductDetailView.as_view(),
        name="product_detail"
    ),
]