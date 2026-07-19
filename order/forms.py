# order/forms.py
from django import forms
from django.utils import timezone
from .models import Order, Coupon, UserAddress


# ==========================================
# لیست استان‌های ایران
# ==========================================
IRAN_STATES = [
    ("آذربایجان شرقی", "آذربایجان شرقی"),
    ("آذربایجان غربی", "آذربایجان غربی"),
    ("اردبیل", "اردبیل"),
    ("اصفهان", "اصفهان"),
    ("البرز", "البرز"),
    ("ایلام", "ایلام"),
    ("بوشهر", "بوشهر"),
    ("تهران", "تهران"),
    ("چهارمحال و بختیاری", "چهارمحال و بختیاری"),
    ("خراسان جنوبی", "خراسان جنوبی"),
    ("خراسان رضوی", "خراسان رضوی"),
    ("خراسان شمالی", "خراسان شمالی"),
    ("خوزستان", "خوزستان"),
    ("زنجان", "زنجان"),
    ("سمنان", "سمنان"),
    ("سیستان و بلوچستان", "سیستان و بلوچستان"),
    ("فارس", "فارس"),
    ("قزوین", "قزوین"),
    ("قم", "قم"),
    ("کردستان", "کردستان"),
    ("کرمان", "کرمان"),
    ("کرمانشاه", "کرمانشاه"),
    ("کهگیلویه و بویراحمد", "کهگیلویه و بویراحمد"),
    ("گلستان", "گلستان"),
    ("گیلان", "گیلان"),
    ("لرستان", "لرستان"),
    ("مازندران", "مازندران"),
    ("مرکزی", "مرکزی"),
    ("هرمزگان", "هرمزگان"),
    ("همدان", "همدان"),
    ("یزد", "یزد"),
]

# لیست شهرهای هر استان
CITIES_BY_STATE = {
    "تهران": ["تهران", "ری", "شهریار", "قدس", "ملارد", "ورامین", "قرچک", "پاکدشت"],
    "اصفهان": ["اصفهان", "کاشان", "خمینی‌شهر", "نجف‌آباد", "فولادشهر", "شاهین‌شهر", "مبارکه", "زرین‌شهر"],
    "مازندران": ["ساری", "بابل", "آمل", "قائم‌شهر", "بابلسر", "نوشهر", "چالوس", "رامسر"],
    "گیلان": ["رشت", "انزلی", "لاهیجان", "آستارا", "رودسر", "فومن", "صومعه‌سرا"],
    "خراسان رضوی": ["مشهد", "نیشابور", "سبزوار", "تربت حیدریه", "کاشمر", "قوچان"],
    "فارس": ["شیراز", "مرودشت", "کازرون", "لار", "فیروزآباد", "جهرم"],
    "خوزستان": ["اهواز", "دزفول", "آبادان", "خرمشهر", "بهبهان", "اندیمشک"],
    "آذربایجان شرقی": ["تبریز", "مراغه", "مرند", "میانه", "اهر", "بستان‌آباد"],
    "آذربایجان غربی": ["ارومیه", "خوی", "بوکان", "مهاباد", "سردشت", "پیرانشهر"],
    "کرمان": ["کرمان", "رفسنجان", "سیرجان", "زرند", "بم", "جیرفت"],
    "کرمانشاه": ["کرمانشاه", "اسلام‌آباد غرب", "سنقر", "هرسین"],
    "هرمزگان": ["بندرعباس", "میناب", "قشم", "کیش", "بندرلنگه"],
    "یزد": ["یزد", "میبد", "اردکان", "بافق", "مهریز", "تفت"],
    "همدان": ["همدان", "ملایر", "نهاوند", "اسدآباد", "تویسرکان"],
    "لرستان": ["خرم‌آباد", "بروجرد", "دورود", "الیگودرز", "کوهدشت"],
    "زنجان": ["زنجان", "ابهر", "خدابنده", "طارم"],
    "سمنان": ["سمنان", "شاهرود", "دامغان", "گرمسار", "میامی"],
    "مرکزی": ["اراک", "ساوه", "خمین", "محلات", "تفرش", "دلیجان"],
    "البرز": ["کرج", "نظرآباد", "تاکستان", "ساوجبلاغ"],
    "کردستان": ["سنندج", "سقز", "مریوان", "بانه", "دیواندره"],
    "اردبیل": ["اردبیل", "پارس‌آباد", "مشگین‌شهر", "بیله‌سوار"],
    "سیستان و بلوچستان": ["زاهدان", "چابهار", "زابل", "ایرانشهر", "خاش"],
    "گلستان": ["گرگان", "گنبد کاووس", "علی‌آباد", "آق‌قلا"],
    "چهارمحال و بختیاری": ["شهرکرد", "بروجن", "فارسان", "لردگان"],
    "بوشهر": ["بوشهر", "برازجان", "جم", "کنگان", "دشتستان"],
    "ایلام": ["ایلام", "دهلران", "ایوان", "آبدانان"],
    "قزوین": ["قزوین", "الوند", "بوئین‌زهرا", "تاکستان"],
    "قم": ["قم", "کهک", "جعفریه"],
    "خراسان جنوبی": ["بیرجند", "قائن", "طبس", "درمیان"],
    "خراسان شمالی": ["بجنورد", "شیروان", "اسفراین", "جاجرم"],
    "کهگیلویه و بویراحمد": ["یاسوج", "گچساران", "دوگنبدان", "دهدشت"],
}


class CheckoutForm(forms.Form):
    """
    فرم تسویه حساب (Checkout) با انتخاب آدرس یا وارد کردن آدرس جدید
    """
    # انتخاب آدرس موجود
    use_existing_address = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'use-existing-address'})
    )
    
    address_id = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'address-select'}),
        label="انتخاب آدرس"
    )
    
    # آدرس جدید
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'خیابان، پلاک، واحد...'}),
        label="آدرس"
    )
    state = forms.ChoiceField(
        required=False,
        choices=[("", "انتخاب استان...")] + IRAN_STATES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'state-select'}),
        label="استان"
    )
    city = forms.ChoiceField(
        required=False,
        choices=[("", "ابتدا استان را انتخاب کنید...")],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'city-select'}),
        label="شهر"
    )
    zip_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد پستی', 'dir': 'ltr'}),
        label="کد پستی"
    )
    
    # کد تخفیف
    coupon_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تخفیف را وارد کنید...',
            'id': 'coupon-input'
        }),
        label="کد تخفیف"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.cart_total = kwargs.pop('cart_total', 0)
        super().__init__(*args, **kwargs)
        
        # پر کردن انتخاب آدرس‌های موجود
        if self.user:
            addresses = UserAddress.objects.filter(user=self.user)
            if addresses.exists():
                choices = [("", "انتخاب آدرس...")]
                for addr in addresses:
                    choices.append((addr.id, f"{addr.address} - {addr.city}"))
                self.fields['address_id'].choices = choices
                
                # اگر آدرس پیش‌فرض وجود دارد، آن را انتخاب کن
                default_address = addresses.filter(is_default=True).first()
                if default_address:
                    self.fields['address_id'].initial = default_address.id
                    self.fields['use_existing_address'].initial = True
            else:
                self.fields['address_id'].choices = [("", "هیچ آدرسی ثبت نشده است")]
                self.fields['use_existing_address'].initial = False

    def clean(self):
        cleaned_data = super().clean()
        use_existing = cleaned_data.get('use_existing_address')
        
        if use_existing:
            # بررسی آدرس انتخاب شده
            address_id = cleaned_data.get('address_id')
            if not address_id:
                raise forms.ValidationError("لطفاً یک آدرس انتخاب کنید.")
            
            try:
                address = UserAddress.objects.get(id=address_id, user=self.user)
                cleaned_data['selected_address'] = address
            except UserAddress.DoesNotExist:
                raise forms.ValidationError("آدرس انتخاب شده نامعتبر است.")
        else:
            # بررسی آدرس جدید
            address = cleaned_data.get('address')
            state = cleaned_data.get('state')
            city = cleaned_data.get('city')
            
            if not address:
                raise forms.ValidationError("لطفاً آدرس را وارد کنید.")
            if not state:
                raise forms.ValidationError("لطفاً استان را انتخاب کنید.")
            if not city:
                raise forms.ValidationError("لطفاً شهر را انتخاب کنید.")
        
        return cleaned_data

    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code')
        if not code:
            return None

        try:
            coupon = Coupon.objects.get(code=code.upper())
        except Coupon.DoesNotExist:
            raise forms.ValidationError("کد تخفیف نامعتبر است.")

        # اعتبارسنجی کد تخفیف
        if not coupon.is_active:
            raise forms.ValidationError("این کد تخفیف غیرفعال است.")

        if coupon.expiration_date and coupon.expiration_date < timezone.now():
            raise forms.ValidationError("کد تخفیف منقضی شده است.")

        if coupon.used_by.count() >= coupon.max_limit_usage:
            raise forms.ValidationError("تعداد استفاده از این کد به پایان رسیده است.")

        if self.user and coupon.used_by.filter(id=self.user.id).exists():
            raise forms.ValidationError("شما قبلاً از این کد تخفیف استفاده کرده‌اید.")

        if coupon.min_purchase_amount and self.cart_total < coupon.min_purchase_amount:
            raise forms.ValidationError(f"حداقل مبلغ خرید برای این کد تخفیف {coupon.min_purchase_amount:,} تومان است.")

        return coupon


class OrderCreateForm(forms.ModelForm):
    """
    فرم ایجاد سفارش (برای ذخیره در دیتابیس)
    """
    class Meta:
        model = Order
        fields = [
            'address',
            'state',
            'city',
            'zip_code',
            'coupon',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.cart_items = kwargs.pop('cart_items', [])
        self.selected_address = kwargs.pop('selected_address', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        order = super().save(commit=False)
        order.user = self.user
        
        # اگر آدرس انتخابی وجود داشته باشد، اطلاعات آن را کپی کن
        if self.selected_address:
            order.address = self.selected_address.address
            order.state = self.selected_address.state
            order.city = self.selected_address.city
            order.zip_code = self.selected_address.zip_code
        
        # محاسبه قیمت کل از سبد خرید
        total_price = sum(item['product'].get_price() * item['quantity'] for item in self.cart_items)
        order.total_price = total_price
        
        # اعمال تخفیف اگر کوپن وجود داشته باشد
        if order.coupon:
            discount_amount = total_price * (order.coupon.discount_percent / 100)
            order.total_price = round(total_price - discount_amount)
            
            # ثبت استفاده از کوپن
            order.coupon.used_by.add(self.user)

        if commit:
            order.save()
            # ذخیره آیتم‌های سفارش
            for item in self.cart_items:
                order.items.create(
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].get_price()
                )
        return order


class CouponApplyForm(forms.Form):
    """
    فرم اعمال کد تخفیف در سبد خرید (AJAX)
    """
    coupon_code = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد تخفیف را وارد کنید...',
            'id': 'coupon-input'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.cart_total = kwargs.pop('cart_total', 0)
        super().__init__(*args, **kwargs)

    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code')
        if not code:
            raise forms.ValidationError("لطفاً کد تخفیف را وارد کنید.")

        try:
            coupon = Coupon.objects.get(code=code.upper())
        except Coupon.DoesNotExist:
            raise forms.ValidationError("کد تخفیف نامعتبر است.")

        # اعتبارسنجی‌ها
        if not coupon.is_active:
            raise forms.ValidationError("این کد تخفیف غیرفعال است.")

        if coupon.expiration_date and coupon.expiration_date < timezone.now():
            raise forms.ValidationError("کد تخفیف منقضی شده است.")

        if coupon.used_by.count() >= coupon.max_limit_usage:
            raise forms.ValidationError("تعداد استفاده از این کد به پایان رسیده است.")

        if self.user and coupon.used_by.filter(id=self.user.id).exists():
            raise forms.ValidationError("شما قبلاً از این کد تخفیف استفاده کرده‌اید.")

        if coupon.min_purchase_amount and self.cart_total < coupon.min_purchase_amount:
            raise forms.ValidationError(f"حداقل مبلغ خرید برای این کد تخفیف {coupon.min_purchase_amount:,} تومان است.")

        return coupon