# order/models.py
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal


class OrderStatusType(models.IntegerChoices):
    PENDING = 1, "Pending"
    SUCCESS = 2, "Success"
    FAILED = 3, "Failed"


class UserAddress(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    
    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Coupon(models.Model):
    code = models.CharField(max_length=100, unique=True)
    discount_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_limit_usage = models.PositiveIntegerField(default=10)
    used_by = models.ManyToManyField('account.User', related_name="coupon_users", blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    min_purchase_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        default=0,
        verbose_name="حداقل مبلغ خرید"
    )
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

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
        is_valid, message = self.is_valid(user, total_amount)
        if not is_valid:
            return None, message
        
        discount_amount = total_amount * (self.discount_percent / 100)
        final_price = total_amount - discount_amount
        
        if user:
            self.used_by.add(user)
        
        return round(final_price), f"{self.discount_percent}% تخفیف"


class Order(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.PROTECT)
    
    # order address information
    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    
    transaction = models.ForeignKey('payment.Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, null=True, blank=True)
    status = models.IntegerField(choices=OrderStatusType.choices, default=OrderStatusType.PENDING.value)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
    
    def calculate_total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())
    
    def __str__(self):
        return f"{self.user.phone} - {self.id}"
    
    def get_status(self):
        return {
            "id": self.status,
            "name": OrderStatusType(self.status).name,
            "label": OrderStatusType(self.status).label,
        }
        
    def get_full_address(self):
        return f"{self.state}, {self.city}, {self.address}"
    
    @property
    def is_successful(self):
        return self.status == OrderStatusType.SUCCESS.value
    
    def get_price(self):
        if self.coupon:            
            return round(self.total_price - (self.total_price * Decimal(self.coupon.discount_percent / 100)))
        else:
            return self.total_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items") 
    product = models.ForeignKey('shop.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.title} - {self.order.id}"