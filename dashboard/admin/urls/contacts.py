# dashboard/admin/urls/contacts.py
from django.urls import path
from ..views.contacts import AdminContactListView, AdminContactDetailView

app_name = "contacts"

urlpatterns = [
    path("contact/list/", AdminContactListView.as_view(), name="contact-list"),
    path("contact/<int:pk>/", AdminContactDetailView.as_view(), name="contact-detail"),
]