from decimal import Decimal

from django import forms
from django.core.validators import MinValueValidator


class WalletDepositForm(forms.Form):
    amount = forms.DecimalField(
        label="مبلغ شارژ",
        min_value=Decimal("1000"),
        max_digits=12,
        decimal_places=0,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "مبلغ را به تومان وارد کنید",
                "min": "1000",
                "step": "1000",
            }
        ),
    )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= 0:
            raise forms.ValidationError(
                "مبلغ باید بیشتر از صفر باشد."
            )

        if amount > Decimal("10000000"):
            raise forms.ValidationError(
                "حداکثر مبلغ شارژ ۱۰ میلیون تومان است."
            )

        return amount