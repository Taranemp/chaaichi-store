from django.urls import path
from ..views.reviews import CustomerReviewListView

app_name = "reviews"

urlpatterns = [
    path("reviews/", CustomerReviewListView.as_view(), name="review-list"),
]