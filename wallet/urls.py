from django.urls import path

from .views import WalletDepositView


app_name = "wallet"


urlpatterns = [
    path(
        "deposit/",
        WalletDepositView.as_view(),
        name="deposit",
    ),
]