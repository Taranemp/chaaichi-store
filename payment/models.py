from django.conf import settings
from django.db import models


class PaymentStatusType(models.IntegerChoices):
    PENDING = 1, "Pending"
    SUCCESS = 2, "Success"
    FAILED = 3, "Failed"
    REFUNDED = 4, "Refunded"


class PaymentMethodType(models.IntegerChoices):
    GATEWAY = 1, "Gateway"
    WALLET = 2, "Wallet"


class PaymentPurposeType(models.IntegerChoices):
    ORDER = 1, "Order"
    WALLET_DEPOSIT = 2, "Wallet Deposit"


class Payment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    method = models.IntegerField(
        choices=PaymentMethodType.choices
    )

    purpose = models.IntegerField(
        choices=PaymentPurposeType.choices
    )

    status = models.IntegerField(
        choices=PaymentStatusType.choices,
        default=PaymentStatusType.PENDING.value
    )

    # Gateway information
    authority = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    reference_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
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
        return (
            f"Payment #{self.id} - "
            f"{self.user} - "
            f"{self.amount:,}"
        )

    @property
    def is_successful(self):
        return (
            self.status ==
            PaymentStatusType.SUCCESS.value
        )

    def get_status(self):
        return {
            "id": self.status,
            "name": PaymentStatusType(self.status).name,
            "label": PaymentStatusType(self.status).label,
        }