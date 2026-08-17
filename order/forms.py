from django import forms
from django.utils import timezone

from .models import Order, Coupon, UserAddress
from payment.models import PaymentMethodType


# =========================================================
# IRAN STATES
# =========================================================

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


# =========================================================
# CITIES BY STATE
# =========================================================

CITIES_BY_STATE = {
    "تهران": [
        "تهران",
        "ری",
        "شهریار",
        "قدس",
        "ملارد",
        "ورامین",
        "قرچک",
        "پاکدشت",
    ],

    "اصفهان": [
        "اصفهان",
        "کاشان",
        "خمینی‌شهر",
        "نجف‌آباد",
        "فولادشهر",
        "شاهین‌شهر",
        "مبارکه",
        "زرین‌شهر",
    ],

    "مازندران": [
        "ساری",
        "بابل",
        "آمل",
        "قائم‌شهر",
        "بابلسر",
        "نوشهر",
        "چالوس",
        "رامسر",
    ],

    "گیلان": [
        "رشت",
        "انزلی",
        "لاهیجان",
        "آستارا",
        "رودسر",
        "فومن",
        "صومعه‌سرا",
    ],

    "خراسان رضوی": [
        "مشهد",
        "نیشابور",
        "سبزوار",
        "تربت حیدریه",
        "کاشمر",
        "قوچان",
    ],

    "فارس": [
        "شیراز",
        "مرودشت",
        "کازرون",
        "لار",
        "فیروزآباد",
        "جهرم",
    ],

    "خوزستان": [
        "اهواز",
        "دزفول",
        "آبادان",
        "خرمشهر",
        "بهبهان",
        "اندیمشک",
    ],

    "آذربایجان شرقی": [
        "تبریز",
        "مراغه",
        "مرند",
        "میانه",
        "اهر",
        "بستان‌آباد",
    ],

    "آذربایجان غربی": [
        "ارومیه",
        "خوی",
        "بوکان",
        "مهاباد",
        "سردشت",
        "پیرانشهر",
    ],

    "کرمان": [
        "کرمان",
        "رفسنجان",
        "سیرجان",
        "زرند",
        "بم",
        "جیرفت",
    ],

    "کرمانشاه": [
        "کرمانشاه",
        "اسلام‌آباد غرب",
        "سنقر",
        "هرسین",
    ],

    "هرمزگان": [
        "بندرعباس",
        "میناب",
        "قشم",
        "کیش",
        "بندرلنگه",
    ],

    "یزد": [
        "یزد",
        "میبد",
        "اردکان",
        "بافق",
        "مهریز",
        "تفت",
    ],

    "همدان": [
        "همدان",
        "ملایر",
        "نهاوند",
        "اسدآباد",
        "تویسرکان",
    ],

    "لرستان": [
        "خرم‌آباد",
        "بروجرد",
        "دورود",
        "الیگودرز",
        "کوهدشت",
    ],

    "زنجان": [
        "زنجان",
        "ابهر",
        "خدابنده",
        "طارم",
    ],

    "سمنان": [
        "سمنان",
        "شاهرود",
        "دامغان",
        "گرمسار",
        "میامی",
    ],

    "مرکزی": [
        "اراک",
        "ساوه",
        "خمین",
        "محلات",
        "تفرش",
        "دلیجان",
    ],

    "البرز": [
        "کرج",
        "نظرآباد",
        "تاکستان",
        "ساوجبلاغ",
    ],

    "کردستان": [
        "سنندج",
        "سقز",
        "مریوان",
        "بانه",
        "دیواندره",
    ],

    "اردبیل": [
        "اردبیل",
        "پارس‌آباد",
        "مشگین‌شهر",
        "بیله‌سوار",
    ],

    "سیستان و بلوچستان": [
        "زاهدان",
        "چابهار",
        "زابل",
        "ایرانشهر",
        "خاش",
    ],

    "گلستان": [
        "گرگان",
        "گنبد کاووس",
        "علی‌آباد",
        "آق‌قلا",
    ],

    "چهارمحال و بختیاری": [
        "شهرکرد",
        "بروجن",
        "فارسان",
        "لردگان",
    ],

    "بوشهر": [
        "بوشهر",
        "برازجان",
        "جم",
        "کنگان",
        "دشتستان",
    ],

    "ایلام": [
        "ایلام",
        "دهلران",
        "ایوان",
        "آبدانان",
    ],

    "قزوین": [
        "قزوین",
        "الوند",
        "بوئین‌زهرا",
        "تاکستان",
    ],

    "قم": [
        "قم",
        "کهک",
        "جعفریه",
    ],

    "خراسان جنوبی": [
        "بیرجند",
        "قائن",
        "طبس",
        "درمیان",
    ],

    "خراسان شمالی": [
        "بجنورد",
        "شیروان",
        "اسفراین",
        "جاجرم",
    ],

    "کهگیلویه و بویراحمد": [
        "یاسوج",
        "گچساران",
        "دوگنبدان",
        "دهدشت",
    ],
}


# =========================================================
# CHECKOUT FORM
# =========================================================

class CheckoutForm(forms.Form):

    # -----------------------------------------------------
    # Existing Address
    # -----------------------------------------------------

    use_existing_address = forms.BooleanField(
        required=False,
        initial=True,
        label="استفاده از آدرس ذخیره شده",
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "id": "use-existing-address",
            }
        ),
    )

    address_id = forms.ChoiceField(
        required=False,
        label="آدرس ذخیره شده",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "address-select",
            }
        ),
    )

    # -----------------------------------------------------
    # New Address
    # -----------------------------------------------------

    receiver_name = forms.CharField(
        required=False,
        max_length=100,
        label="نام گیرنده",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "نام و نام خانوادگی گیرنده",
            }
        ),
    )

    receiver_phone = forms.CharField(
        required=False,
        max_length=20,
        label="شماره گیرنده",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "شماره تماس گیرنده",
            }
        ),
    )

    address = forms.CharField(
        required=False,
        max_length=250,
        label="آدرس کامل",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "خیابان، پلاک، واحد",
            }
        ),
    )

    state = forms.ChoiceField(
        required=False,
        label="استان",
        choices=[
            ("", "انتخاب استان...")
        ] + IRAN_STATES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "state-select",
            }
        ),
    )

    city = forms.ChoiceField(
        required=False,
        label="شهر",
        choices=[
            ("", "انتخاب شهر...")
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "city-select",
            }
        ),
    )

    zip_code = forms.CharField(
        required=False,
        max_length=50,
        label="کد پستی",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "کد پستی",
            }
        ),
    )

    # -----------------------------------------------------
    # Coupon
    # -----------------------------------------------------

    coupon_code = forms.CharField(
        required=False,
        max_length=100,
        label="کد تخفیف",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "کد تخفیف",
                "id": "coupon-input",
            }
        ),
    )

    # -----------------------------------------------------
    # Payment Method
    # -----------------------------------------------------

    payment_method = forms.ChoiceField(
        required=True,
        label="روش پرداخت",
        choices=[
            (
                PaymentMethodType.GATEWAY.value,
                "پرداخت آنلاین",
            ),
            (
                PaymentMethodType.WALLET.value,
                "پرداخت از کیف پول",
            ),
        ],
        widget=forms.RadioSelect(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    # =====================================================
    # INIT
    # =====================================================

    def __init__(
        self,
        *args,
        user=None,
        cart_total=0,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.user = user
        self.cart_total = cart_total

        # -------------------------------------------------
        # User Addresses
        # -------------------------------------------------

        if self.user:

            addresses = UserAddress.objects.filter(
                user=self.user
            )

            self.fields[
                "address_id"
            ].choices = [
                (
                    str(address.id),
                    f"{address.city} - {address.address}",
                )
                for address in addresses
            ]

        # -------------------------------------------------
        # Cities
        # -------------------------------------------------

        state = self.data.get("state")

        if state:

            cities = CITIES_BY_STATE.get(
                state,
                [],
            )

            self.fields[
                "city"
            ].choices = [
                (
                    city,
                    city,
                )
                for city in cities
            ]

    # =====================================================
    # CLEAN COUPON
    # =====================================================

    def clean_coupon_code(self):

        code = self.cleaned_data.get(
            "coupon_code"
        )

        if not code:
            return None

        code = code.strip().upper()

        try:

            coupon = Coupon.objects.get(
                code=code
            )

        except Coupon.DoesNotExist:

            raise forms.ValidationError(
                "کد تخفیف اشتباه است."
            )

        valid, message = coupon.is_valid(
            user=self.user,
            total_amount=self.cart_total,
        )

        if not valid:

            raise forms.ValidationError(
                message
            )

        return coupon

    # =====================================================
    # CLEAN
    # =====================================================

    def clean(self):

        cleaned_data = super().clean()

        use_existing = cleaned_data.get(
            "use_existing_address"
        )

        # =================================================
        # EXISTING ADDRESS
        # =================================================

        if use_existing:

            address_id = cleaned_data.get(
                "address_id"
            )

            if not address_id:

                raise forms.ValidationError(
                    "لطفاً یک آدرس انتخاب کنید."
                )

            try:

                selected_address = (
                    UserAddress.objects.get(
                        id=address_id,
                        user=self.user,
                    )
                )

            except UserAddress.DoesNotExist:

                raise forms.ValidationError(
                    "آدرس انتخاب شده معتبر نیست."
                )

            cleaned_data[
                "selected_address"
            ] = selected_address

        # =================================================
        # NEW ADDRESS
        # =================================================

        else:

            required_fields = [
                "receiver_name",
                "receiver_phone",
                "address",
                "state",
                "city",
                "zip_code",
            ]

            for field in required_fields:

                if not cleaned_data.get(field):

                    raise forms.ValidationError(
                        "لطفاً اطلاعات ارسال را کامل کنید."
                    )

            # -------------------------------------------------
            # Validate city belongs to selected state
            # -------------------------------------------------

            state = cleaned_data.get(
                "state"
            )

            city = cleaned_data.get(
                "city"
            )

            valid_cities = CITIES_BY_STATE.get(
                state,
                [],
            )

            if city not in valid_cities:

                raise forms.ValidationError(
                    "شهر انتخاب شده با استان انتخابی مطابقت ندارد."
                )

            cleaned_data[
                "selected_address"
            ] = None

        # =================================================
        # PAYMENT METHOD
        # =================================================

        payment_method = cleaned_data.get(
            "payment_method"
        )

        valid_payment_methods = {
            str(
                PaymentMethodType.GATEWAY.value
            ),
            str(
                PaymentMethodType.WALLET.value
            ),
        }

        if payment_method not in valid_payment_methods:

            raise forms.ValidationError(
                "روش پرداخت انتخاب شده معتبر نیست."
            )

        # =================================================
        # NORMALIZE PAYMENT METHOD
        # =================================================

        cleaned_data[
            "payment_method"
        ] = int(payment_method)

        return cleaned_data