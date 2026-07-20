from django.urls import path
from ..views.wishlists import CustomerWishlistListView, CustomerWishlistDeleteView

app_name = "wishlists"

urlpatterns = [
    path("wishlist/", CustomerWishlistListView.as_view(), name="wishlist-list"),
    path("wishlist/<int:pk>/delete/", CustomerWishlistDeleteView.as_view(), name="wishlist-delete"),
]