# order/models.py

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal


class OrderStatusType(models.IntegerChoices):
    PENDING = 1, "Pending"
    SUCCESS = 2, "Success"
    FAILED = 3, "Failed"


# =========================
# User Address
# =========================

class UserAddress(models.Model):

    user = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    receiver_name = models.CharField(
        max_length=100,
        verbose_name="نام گیرنده",
        null=True,
        blank=True
    )

    receiver_phone = models.CharField(
        max_length=20,
        verbose_name="شماره گیرنده",
        null=True,
        blank=True
    )

    address = models.CharField(
        max_length=250
    )

    state = models.CharField(
        max_length=50
    )

    city = models.CharField(
        max_length=50
    )

    zip_code = models.CharField(
        max_length=50
    )

    is_default = models.BooleanField(
        default=False
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = ["-created_date"]


    def __str__(self):
        return f"{self.receiver_name} - {self.city}"



# =========================
# Coupon
# =========================

class Coupon(models.Model):

    code = models.CharField(
        max_length=100,
        unique=True
    )

    discount_percent = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    max_limit_usage = models.PositiveIntegerField(
        default=10
    )

    used_by = models.ManyToManyField(
        "account.User",
        related_name="coupon_users",
        blank=True
    )

    expiration_date = models.DateTimeField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    min_purchase_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="حداقل مبلغ خرید"
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"


    def is_valid(self, user=None, total_amount=0):

        from django.utils import timezone

        if self.expiration_date and self.expiration_date < timezone.now():
            return False, "منقضی شده"

        if not self.is_active:
            return False, "غیرفعال"

        if self.used_by.count() >= self.max_limit_usage:
            return False, "تعداد استفاده تکمیل شده"

        if user and self.used_by.filter(id=user.id).exists():
            return False, "قبلاً استفاده شده"

        if total_amount < self.min_purchase_amount:
            return False, f"حداقل مبلغ {self.min_purchase_amount} تومان"

        return True, "معتبر"



    def apply(self, user, total_amount):

        is_valid, message = self.is_valid(
            user,
            total_amount
        )

        if not is_valid:
            return None, message


        discount_amount = (
            Decimal(total_amount) *
            Decimal(self.discount_percent) /
            Decimal(100)
        )


        final_price = (
            Decimal(total_amount) -
            discount_amount
        )


        if user:
            self.used_by.add(user)


        return round(final_price), f"{self.discount_percent}% تخفیف"



# =========================
# Order
# =========================

class Order(models.Model):

    user = models.ForeignKey(
        "account.User",
        on_delete=models.PROTECT
    )

    payment = models.ForeignKey(
    "payment.Payment",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="orders",
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    

    receiver_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )


    receiver_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )


    address = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )


    state = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )


    city = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )


    zip_code = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )


    items_total = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    products_discount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    coupon_discount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    status = models.IntegerField(
        choices=OrderStatusType.choices,
        default=OrderStatusType.PENDING.value
    )


    created_date = models.DateTimeField(
        auto_now_add=True
    )


    updated_date = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = ["-created_date"]


    def __str__(self):
        return f"Order #{self.id} - {self.user}"


    @property
    def is_successful(self):
        return self.status == OrderStatusType.SUCCESS.value


    def get_status(self):

        return {
            "id": self.status,
            "name": OrderStatusType(self.status).name,
            "label": OrderStatusType(self.status).label,
        }


    def get_full_address(self):

        return (
            f"{self.state}، "
            f"{self.city}، "
            f"{self.address}"
        )



# =========================
# Order Item
# =========================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )


    product = models.ForeignKey(
        "shop.Product",
        on_delete=models.PROTECT
    )


    product_title = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )


    product_slug = models.SlugField(
        max_length=255,
        null=True,
        blank=True
    )


    quantity = models.PositiveIntegerField(
        default=1
    )


    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )


    created_date = models.DateTimeField(
        auto_now_add=True
    )


    updated_date = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = ["id"]


    def __str__(self):
        return f"{self.product_title} × {self.quantity}"


    @property
    def total_original_price(self):
        return (
            self.original_price *
            self.quantity
        )


    @property
    def total_discount(self):
        return (
            self.discount_amount *
            self.quantity
        )


    @property
    def subtotal(self):
        return (
            self.unit_price *
            self.quantity
        )