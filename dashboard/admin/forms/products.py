from django import forms
from django.utils.text import slugify
from shop.models import Product, ProductImage, Category, Brand, Grade, PackageType


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "grade",
            "package",
            "title",
            "slug",
            "image",
            "description",
            "brief_description",
            "stock",
            "status",
            "price",
            "discount_percent",
        ]
        widgets = {
            'slug': forms.HiddenInput(),
            # ویجت چندانتخابی معمولی؛ ظاهرش رو با Choices.js تو تمپلیت می‌سازیم
            'category': forms.SelectMultiple(attrs={'class': 'js-choice-multiple'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        self.fields['slug'].required = False

        for field_name, field in self.fields.items():
            if field_name not in ['slug', 'category']:
                field.widget.attrs['class'] = 'form-control'

        self.fields['brand'].widget.attrs['class'] = 'form-select'
        self.fields['grade'].widget.attrs['class'] = 'form-select'
        self.fields['package'].widget.attrs['class'] = 'form-select'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['description'].widget.attrs['id'] = 'ckeditor'

        self.fields['stock'].widget.attrs['type'] = 'number'
        self.fields['stock'].widget.attrs['min'] = 0
        self.fields['price'].widget.attrs['type'] = 'number'
        self.fields['price'].widget.attrs['min'] = 0
        self.fields['discount_percent'].widget.attrs['type'] = 'number'
        self.fields['discount_percent'].widget.attrs['min'] = 0
        self.fields['discount_percent'].widget.attrs['max'] = 100

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')

        if not slug and title:
            slug = slugify(title, allow_unicode=True)

        if slug:
            import re
            slug = re.sub(r'[^\w\-]', '-', slug).strip('-')

            original_slug = slug
            counter = 1
            instance = getattr(self, 'instance', None)
            while Product.objects.filter(slug=slug).exclude(pk=instance.pk if instance else None).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

        return slug


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['accept'] = 'image/*'