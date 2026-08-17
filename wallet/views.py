from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from payment.models import (
    Payment,
    PaymentMethodType,
    PaymentPurposeType,
    PaymentStatusType,
)
from wallet.forms import WalletDepositForm


class WalletDepositView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        form = WalletDepositForm(request.POST)

        if not form.is_valid():
            messages.error(
                request,
                "مبلغ واردشده معتبر نیست."
            )
            return redirect("dashboard:customer:wallet")

        amount = form.cleaned_data["amount"]

        if amount <= 0:
            messages.error(
                request,
                "مبلغ شارژ باید بیشتر از صفر باشد."
            )
            return redirect("dashboard:customer:wallet")

        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            method=PaymentMethodType.GATEWAY.value,
            purpose=PaymentPurposeType.WALLET_DEPOSIT.value,
            status=PaymentStatusType.PENDING.value,
            description="شارژ کیف پول",
        )

        return redirect(
            "payment:start_gateway",  
            
            pk=payment.pk,
        )