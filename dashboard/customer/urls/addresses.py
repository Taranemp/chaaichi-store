from django.urls import path
from ..views.addresses import (
    CustomerAddressListView,
    CustomerAddressCreateView,
    CustomerAddressEditView,
    CustomerAddressDeleteView,
)

app_name = "addresses"

urlpatterns = [
    path("address/list/", CustomerAddressListView.as_view(), name="address-list"),
    path("address/create/", CustomerAddressCreateView.as_view(), name="address-create"),
    path("address/<int:pk>/edit/", CustomerAddressEditView.as_view(), name="address-edit"),
    path("address/<int:pk>/delete/", CustomerAddressDeleteView.as_view(), name="address-delete"),
]