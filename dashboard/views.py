# dashboard/views.py
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from account.models import UserType


class DashboardHomeView(LoginRequiredMixin, RedirectView):
    """Route users to the correct dashboard based on account type."""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user

        if user.type == UserType.customer.value:
            return reverse_lazy("dashboard:customer:home")

        if user.type in (UserType.admin.value, UserType.superuser.value):
            return reverse_lazy("dashboard:admin:home")

        return reverse_lazy("account:login")
