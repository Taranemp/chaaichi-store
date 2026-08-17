from django.urls import path
from ..views import WalletDashboardView


urlpatterns = [
    path(
        "",
        WalletDashboardView.as_view(),
        name="wallet",
    ),
]