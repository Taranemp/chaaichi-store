from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from wallet.forms import WalletDepositForm
from wallet.services import WalletService


class WalletDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customer/wallet/wallet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wallet = WalletService.get_or_create_wallet(
            self.request.user
        )

        # دریافت تراکنش‌های کیف پول به ترتیب جدیدترین
        transactions = wallet.transactions.all().order_by("-created_date")

        context["wallet"] = wallet
        context["balance"] = wallet.balance
        context["transactions"] = transactions
        context["form"] = WalletDepositForm()

        return context