# dashboard/customer/urls/generals.py
from django.urls import path
from ..views import CustomerDashboardHomeView

app_name = "customer"

urlpatterns = [
    path("", CustomerDashboardHomeView.as_view(), name="home"),
]