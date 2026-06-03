from decimal import Decimal
from django.core.exceptions import ValidationError


def validate_positive_amount(value):
    """Amount must not be negative or zero"""
    if value <= 0:
        raise ValidationError("Amount must be greater than zero")


def validate_max_purchase_amount(value, max_amount=Decimal('10000000')):
    """Prevent too large purchases (security)"""
    if value > max_amount:
        raise ValidationError(f"Purchase amount cannot exceed {max_amount:,} Toman")


def validate_duplicate_transaction(user, amount, minutes=5):
    """Prevent duplicate requests in a short time period"""
    from .models import Transaction, TransactionStatusType
    from django.utils import timezone
    from datetime import timedelta

    time_threshold = timezone.now() - timedelta(minutes=minutes)
    recent = Transaction.objects.filter(
        user=user,
        amount=amount,
        status=TransactionStatusType.SUCCESS.value,
        created_date__gte=time_threshold
    ).count()

    if recent > 3:
        raise ValidationError("Too many requests. Please try again later.")