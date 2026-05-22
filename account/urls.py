from django.urls import path, include
from .views import SignUpView, CustomLoginView, CustomLogoutView

app_name = 'account'

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),

    path("", include("django.contrib.auth.urls")),
]
