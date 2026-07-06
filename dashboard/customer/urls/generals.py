# dashboard/customer/urls/generals.py
from django.urls import path
from ..views import CustomerDashboardHomeView

urlpatterns = [
    path("home/", CustomerDashboardHomeView.as_view(), name="home"),
]