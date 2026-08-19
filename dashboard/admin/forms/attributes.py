from django import forms
from django.utils.text import slugify
from shop.models import Grade, PackageType


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['name', 'level']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام درجه کیفی (مثلاً: ممتاز، سرگل، درجه یک)'
            }),
            'level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'اولویت/سطح کیفیت (مثلاً: 1)'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name, allow_unicode=True)
        if commit:
            instance.save()
        return instance


class PackageTypeForm(forms.ModelForm):
    class Meta:
        model = PackageType
        fields = ['name', 'weight_grams']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نوع بسته‌بندی (مثلاً: پاکتی، قوطی فلزی، کادویی)'
            }),
            'weight_grams': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'وزن به گرم (اختیاری - مثلاً: 500)'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name, allow_unicode=True)
        if commit:
            instance.save()
        return instance