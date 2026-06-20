from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("add/", views.AddToCartView.as_view(), name="add"),
    path("remove/", views.RemoveFromCartView.as_view(), name="remove"),
    path("update/", views.UpdateCartView.as_view(), name="update"),
    path("clear/", views.ClearCartView.as_view(), name="clear"),
    path("summary/", views.CartSummaryView.as_view(), name="summary"),
]
