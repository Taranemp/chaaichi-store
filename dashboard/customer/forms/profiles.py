# dashboard/customer/forms/profiles.py
from django.contrib.auth import forms as auth_forms
from django import forms
from django.utils.translation import gettext_lazy as _
from account.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomerPasswordChangeForm(auth_forms.PasswordChangeForm):
    """فرم تغییر رمز عبور مشتری"""
    
    error_messages = {
        "password_incorrect": _("پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید."),
        "password_mismatch": _("دو پسورد ورودی با همدیگر مطابقت ندارند"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control text-center'
        self.fields['old_password'].widget.attrs['placeholder'] = "پسورد قبلی خود را وارد نمایید"
        self.fields['new_password1'].widget.attrs['class'] = 'form-control text-center'
        self.fields['new_password1'].widget.attrs['placeholder'] = "پسورد جدید خود را وارد نمایید"
        self.fields['new_password2'].widget.attrs['class'] = 'form-control text-center'
        self.fields['new_password2'].widget.attrs['placeholder'] = "پسورد جدید را مجدد وارد نمایید"


class CustomerProfileEditForm(forms.ModelForm):
    """فرم ویرایش پروفایل مشتری با امکان تغییر شماره و ایمیل"""
    
    phone = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={'class': 'form-control text-center', 'dir': 'ltr'}),
        required=True,
        label="شماره تماس"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        required=False,
        label="ایمیل"
    )

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'نام خود را وارد نمایید'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'نام خانوادگی را وارد نمایید'
        
        # اگر کاربر وجود داشته باشد، اطلاعات شماره و ایمیل را پر کن
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # ذخیره اطلاعات کاربر
        user = profile.user
        user.phone = self.cleaned_data.get('phone')
        user.email = self.cleaned_data.get('email')
        
        if commit:
            user.save()
            profile.save()
        
        return profile