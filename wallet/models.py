from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class WalletTransactionType(models.IntegerChoices):
    DEPOSIT = 1, "Deposit"
    PURCHASE = 2, "Purchase"
    REFUND = 3, "Refund"


class WalletTransactionStatus(models.IntegerChoices):
    PENDING = 1, "Pending"
    SUCCESS = 2, "Success"
    FAILED = 3, "Failed"


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)]
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def __str__(self):
        return f"{self.user.phone} - {self.balance:,} Toman"

    def has_sufficient_balance(self, amount):
        return self.balance >= amount


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(1)]
    )

    transaction_type = models.IntegerField(
        choices=WalletTransactionType.choices
    )

    status = models.IntegerField(
        choices=WalletTransactionStatus.choices,
        default=WalletTransactionStatus.PENDING.value
    )

    reference_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return (
            f"{self.wallet.user.phone} - "
            f"{self.amount:,} - "
            f"{self.get_transaction_type_display()}"
        )