from django import forms
from django.utils.text import slugify
from shop.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description']  # فیلد slug از اینجا حذف شد
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان دسته‌بندی را وارد کنید'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات کوتاه دسته‌بندی...'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # اگر اسلاگ خالی بود یا در حال ساخت آیتم جدید بودیم، اسلاگ خودکار می‌سازیم
        if not instance.slug:
            # allow_unicode=True باعث می‌شود کلمات فارسی هم در اسلاگ پشتیبانی شوند
            instance.slug = slugify(instance.title, allow_unicode=True)
        if commit:
            instance.save()
        return instance