# dashboard/admin/forms/users.py
from django import forms
from django.contrib.auth import get_user_model
from account.models import Profile

User = get_user_model()


class UserForm(forms.ModelForm):
    """فرم ویرایش کاربر در پنل ادمین"""
    
    # فیلدهای پروفایل
    first_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'})
    )
    last_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'})
    )

    class Meta:
        model = User
        fields = [
            "phone",
            "email",
            "is_active",
            "is_verified",
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control text-center', 'dir': 'ltr'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # اگر کاربر وجود داشته باشد، اطلاعات پروفایل را پر کن
        if self.instance and self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields['first_name'].initial = profile.first_name
                self.fields['last_name'].initial = profile.last_name
            except Profile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # ذخیره اطلاعات پروفایل
            profile, created = Profile.objects.get_or_create(user=user)
            profile.first_name = self.cleaned_data.get('first_name', '')
            profile.last_name = self.cleaned_data.get('last_name', '')
            profile.save()
        
        return user