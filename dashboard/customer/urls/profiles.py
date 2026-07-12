from django.urls import path
from ..views.profiles import (
    CustomerSecurityEditView,
    CustomerProfileEditView,
    CustomerProfileImageEditView,
)

app_name = "profiles"

urlpatterns = [
    path("security/edit/", CustomerSecurityEditView.as_view(), name="security-edit"),
    path("profile/edit/", CustomerProfileEditView.as_view(), name="profile-edit"),
    path("profile/image/edit/", CustomerProfileImageEditView.as_view(), name="profile-image-edit"),
]