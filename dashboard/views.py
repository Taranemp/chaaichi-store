from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.urls import reverse_lazy



class DashboardHomeView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_staff:
            return reverse_lazy("dashboard:admin:home")

        return reverse_lazy("dashboard:customer:home")