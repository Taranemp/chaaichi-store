from django import forms
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # کلاس‌های Bootstrap به همه فیلدها
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['brief_description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['id'] = 'ckeditor'
        self.fields['stock'].widget.attrs['class'] = 'form-control'
        self.fields['stock'].widget.attrs['type'] = 'number'
        self.fields['stock'].widget.attrs['min'] = 0
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['price'].widget.attrs['type'] = 'number'
        self.fields['price'].widget.attrs['min'] = 0
        self.fields['discount_percent'].widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs['type'] = 'number'
        self.fields['discount_percent'].widget.attrs['min'] = 0
        self.fields['discount_percent'].widget.attrs['max'] = 100
        
        # فیلدهای انتخاب‌شونده (select)
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['category'].widget.attrs['multiple'] = True  # ManyToMany
        self.fields['brand'].widget.attrs['class'] = 'form-select'
        self.fields['grade'].widget.attrs['class'] = 'form-select'
        self.fields['package'].widget.attrs['class'] = 'form-select'


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = [
            "file",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['accept'] = 'image/png, image/jpg, image/jpeg, image/webp'