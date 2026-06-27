from django.urls import path
from ..views.profiles import (
    AdminSecurityEditView,
    AdminProfileEditView,
    AdminProfileImageEditView,
)

app_name = "profiles"

urlpatterns = [
    path("security/edit/", AdminSecurityEditView.as_view(), name="security-edit"),
    path("profile/edit/", AdminProfileEditView.as_view(), name="profile-edit"),
    path("profile/image/edit/", AdminProfileImageEditView.as_view(), name="profile-image-edit"),
]