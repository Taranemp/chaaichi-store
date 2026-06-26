from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(forms.ModelForm):
    fullname = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ("phone", "email")
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control", "dir": "ltr"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "dir": "ltr"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        fullname = self.cleaned_data.get("fullname")

        user.set_password(password)

        if commit:
            user.save()
            # ذخیره fullname در پروفایل
            if hasattr(user, 'profile'):
                user.profile.first_name = fullname
                user.profile.save()

        return user