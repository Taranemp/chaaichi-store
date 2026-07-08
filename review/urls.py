from django.urls import path
from .views import SubmitReviewView

app_name = "review"

urlpatterns = [
    path("product/<int:product_id>/submit/", SubmitReviewView.as_view(), name="submit"),
]