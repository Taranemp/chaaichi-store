from django.urls import path
from ..views.users import (
    AdminUserListView,
    AdminUserUpdateView,
    AdminUserDeleteView,
)

app_name = "users"

urlpatterns = [
    path("users/", AdminUserListView.as_view(), name="user-list"),
    path("users/<int:pk>/edit/", AdminUserUpdateView.as_view(), name="user-edit"),
    path("users/<int:pk>/delete/", AdminUserDeleteView.as_view(), name="user-delete"),
]