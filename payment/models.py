# payment/models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class TransactionStatusType(models.IntegerChoices):
    PENDING = 1, "Pending"
    SUCCESS = 2, "Success"
    FAILED = 3, "Failed"
    REFUNDED = 4, "Refunded"


class TransactionType(models.IntegerChoices):
    PURCHASE = 1, "Purchase"
    DEPOSIT = 2, "Deposit"
    REFUND = 3, "Refund"


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=5000000
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone} - {self.balance:,} Toman"

    def has_sufficient_balance(self, amount):
        return self.balance >= amount

    def deduct(self, amount):
        if self.has_sufficient_balance(amount):
            self.balance -= amount
            self.save()
            return True
        return False

    def add(self, amount):
        self.balance += amount
        self.save()


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.IntegerField(
        choices=TransactionStatusType.choices,
        default=TransactionStatusType.PENDING.value
    )
    transaction_type = models.IntegerField(
        choices=TransactionType.choices,
        default=TransactionType.PURCHASE.value
    )
    reference_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.user.phone} - {self.amount:,} - {self.get_transaction_type_display()}"



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    """بعد از ساخت کاربر جدید، کیف پول برایش بساز"""
    if created:
        Wallet.objects.create(user=instance, balance=5000000)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_wallet(sender, instance, **kwargs):
    """بعد از ذخیره کاربر، کیف پول را هم ذخیره کن"""
    if hasattr(instance, 'wallet'):
        instance.wallet.save()