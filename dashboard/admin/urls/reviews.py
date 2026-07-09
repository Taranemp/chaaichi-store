from django.urls import path
from ..views.reviews import AdminReviewListView, AdminReviewEditView

app_name = "reviews"  

urlpatterns = [
    path("review/list/", AdminReviewListView.as_view(), name="review-list"),
    path("review/<int:pk>/edit/", AdminReviewEditView.as_view(), name="review-edit"),
]