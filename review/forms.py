from django import forms
from .models import Review, ReviewStatusType


class SubmitReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rate', 'comment']
        widgets = {
            'rate': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'نظر خود را در مورد این محصول بنویسید...'
            }),
        }
        error_messages = {
            'comment': {
                'required': 'لطفاً نظر خود را وارد کنید',
            },
            'rate': {
                'required': 'لطفاً امتیاز خود را انتخاب کنید',
            },
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        self.fields['rate'].widget.attrs['class'] = 'form-select'
        self.fields['comment'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        
        if self.user and self.product:
            if Review.objects.filter(user=self.user, product=self.product).exists():
                raise forms.ValidationError("شما قبلاً برای این محصول نظر داده‌اید.")
        
        return cleaned_data

    def save(self, commit=True):
        """ذخیره نظر با کاربر و محصول مشخص"""
        review = super().save(commit=False) 
        review.user = self.user
        review.product = self.product
        review.status = ReviewStatusType.PENDING.value

        if commit:
            review.save()
        return review