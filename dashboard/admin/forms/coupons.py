from django import forms
from order.models import Coupon


class CouponForm(forms.ModelForm):
    expiration_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )

    class Meta:
        model = Coupon
        fields = [
            "code",
            "discount_percent",
            "max_limit_usage",
            "expiration_date",
            "is_active",
            "description",
            "min_purchase_amount",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # کلاس‌های Bootstrap
        self.fields['code'].widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs['type'] = 'number'
        self.fields['discount_percent'].widget.attrs['min'] = 0
        self.fields['discount_percent'].widget.attrs['max'] = 100
        
        self.fields['max_limit_usage'].widget.attrs['class'] = 'form-control'
        self.fields['max_limit_usage'].widget.attrs['type'] = 'number'
        self.fields['max_limit_usage'].widget.attrs['min'] = 1
        
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = 3
        
        self.fields['min_purchase_amount'].widget.attrs['class'] = 'form-control'
        self.fields['min_purchase_amount'].widget.attrs['type'] = 'number'
        self.fields['min_purchase_amount'].widget.attrs['min'] = 0