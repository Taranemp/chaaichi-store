from django import forms
from .models import Review, ReviewStatusType


class SubmitReviewForm(forms.ModelForm):
    # چون فیلد rate تو مدل یه IntegerField ساده‌ست (بدون choices)،
    # باید صریحاً choices رو اینجا تعریف کنیم وگرنه ویجت Select خالی می‌مونه
    rate = forms.ChoiceField(
        choices=[
            (5, "★★★★★ عالی"),
            (4, "★★★★ خوب"),
            (3, "★★★ متوسط"),
            (2, "★★ ضعیف"),
            (1, "★ بسیار ضعیف"),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="امتیاز شما",
    )

    class Meta:
        model = Review
        fields = ['rate', 'comment']
        widgets = {
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