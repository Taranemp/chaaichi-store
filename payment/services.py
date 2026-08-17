from decimal import Decimal

from django.db import transaction

from .models import (
    Payment,
    PaymentStatusType,
    PaymentMethodType,
    PaymentPurposeType,
)

from .gateway_service import GatewayService
from wallet.services import WalletService


class PaymentService:

    # =========================================================
    # CREATE PAYMENT
    # =========================================================

    @staticmethod
    def create_payment(
        user,
        amount,
        method,
        purpose,
        description="",
    ):
        amount = Decimal(amount)

        if amount <= 0:
            return False, "مبلغ پرداخت باید بیشتر از صفر باشد", None

        if method not in (
            PaymentMethodType.GATEWAY.value,
            PaymentMethodType.WALLET.value,
        ):
            return False, "روش پرداخت نامعتبر است", None

        if purpose not in (
            PaymentPurposeType.ORDER.value,
            PaymentPurposeType.WALLET_DEPOSIT.value,
        ):
            return False, "هدف پرداخت نامعتبر است", None

        payment = Payment.objects.create(
            user=user,
            amount=amount,
            method=method,
            purpose=purpose,
            status=PaymentStatusType.PENDING.value,
            description=description,
        )

        return True, "پرداخت ایجاد شد", payment

    # =========================================================
    # START GATEWAY PAYMENT
    # =========================================================

    @staticmethod
    def start_gateway_payment(payment):

        if not payment:
            return False, "پرداخت پیدا نشد", None

        if payment.method != PaymentMethodType.GATEWAY.value:
            return False, "این پرداخت از نوع درگاه نیست", None

        if payment.status != PaymentStatusType.PENDING.value:
            return False, "این پرداخت دیگر قابل انجام نیست", None

        if payment.amount <= 0:
            return False, "مبلغ پرداخت نامعتبر است", None

        try:
            success, message, result = (
                GatewayService.create_payment_request(payment)
            )

        except Exception as exc:
            return (
                False,
                f"خطا در ارتباط با درگاه پرداخت: {exc}",
                None,
            )

        if not success:
            return False, message, None

        return (
            True,
            message,
            {
                "payment_url": result["payment_url"],
                "authority": result["authority"],
                "payment": payment,
            },
        )

    # =========================================================
    # VERIFY GATEWAY PAYMENT
    # =========================================================

    @staticmethod
    def verify_gateway_payment(
        payment,
        authority,
    ):

        if not payment:
            return False, "پرداخت پیدا نشد", None

        if payment.method != PaymentMethodType.GATEWAY.value:
            return False, "این پرداخت از نوع درگاه نیست", None

        if payment.status == PaymentStatusType.SUCCESS.value:
            return (
                True,
                "این پرداخت قبلاً تأیید شده است",
                payment,
            )

        if payment.status != PaymentStatusType.PENDING.value:
            return (
                False,
                "این پرداخت دیگر قابل پردازش نیست",
                payment,
            )

        if not authority:
            return False, "کد Authority دریافت نشد", None

        if payment.authority != authority:
            return False, "اطلاعات پرداخت معتبر نیست", None

        try:
            success, message, verified_payment = (
                GatewayService.verify_payment(payment)
            )

        except Exception as exc:
            return (
                False,
                f"خطا در ارتباط با درگاه: {exc}",
                payment,
            )

        if not success:
            return False, message, verified_payment

        return (
            True,
            message,
            verified_payment,
        )

    # =========================================================
    # MARK GATEWAY FAILED
    # =========================================================

    @staticmethod
    def mark_gateway_failed(payment):

        if not payment:
            return False

        if payment.status != PaymentStatusType.PENDING.value:
            return False

        payment.status = PaymentStatusType.FAILED.value

        payment.save(
            update_fields=[
                "status",
                "updated_date",
            ]
        )

        return True

    # =========================================================
    # WALLET PAYMENT
    # =========================================================

    @staticmethod
    def pay_with_wallet(payment):

        if not payment:
            return False, "پرداخت پیدا نشد", None

        if payment.method != PaymentMethodType.WALLET.value:
            return False, "این پرداخت از نوع کیف پول نیست", None

        if payment.purpose != PaymentPurposeType.ORDER.value:
            return (
                False,
                "پرداخت کیف پول فقط برای سفارش قابل استفاده است",
                None,
            )

        if payment.status != PaymentStatusType.PENDING.value:
            return (
                False,
                "این پرداخت دیگر قابل انجام نیست",
                None,
            )

        with transaction.atomic():

            locked_payment = (
                Payment.objects
                .select_for_update()
                .get(pk=payment.pk)
            )

            if (
                locked_payment.status
                != PaymentStatusType.PENDING.value
            ):
                return (
                    False,
                    "این پرداخت قبلاً پردازش شده است",
                    locked_payment,
                )

            success, message, wallet_transaction = (
                WalletService.pay(
                    user=locked_payment.user,
                    amount=locked_payment.amount,
                    reference_id=(
                        f"PAYMENT-{locked_payment.pk}"
                    ),
                    description="پرداخت سفارش با کیف پول",
                )
            )

            if not success:
                return (
                    False,
                    message,
                    locked_payment,
                )

            locked_payment.status = (
                PaymentStatusType.SUCCESS.value
            )

            locked_payment.reference_id = (
                wallet_transaction.reference_id
                if wallet_transaction
                else f"PAYMENT-{locked_payment.pk}"
            )

            locked_payment.save(
                update_fields=[
                    "status",
                    "reference_id",
                    "updated_date",
                ]
            )

            return (
                True,
                "پرداخت با کیف پول با موفقیت انجام شد",
                locked_payment,
            )

    # =========================================================
    # REFUND
    # =========================================================

    @staticmethod
    def refund_to_wallet(
        payment,
        amount=None,
        description="",
    ):

        if not payment:
            return False, "پرداخت پیدا نشد", None

        if payment.status != PaymentStatusType.SUCCESS.value:
            return (
                False,
                "فقط پرداخت موفق قابل بازگشت است",
                None,
            )

        if amount is None:
            amount = payment.amount

        amount = Decimal(amount)

        if amount <= 0:
            return False, "مبلغ بازگشت نامعتبر است", None

        if amount > payment.amount:
            return (
                False,
                "مبلغ بازگشت نمی‌تواند بیشتر از مبلغ پرداخت باشد",
                None,
            )

        with transaction.atomic():

            locked_payment = (
                Payment.objects
                .select_for_update()
                .get(pk=payment.pk)
            )

            success, message, wallet_transaction = (
                WalletService.refund(
                    user=locked_payment.user,
                    amount=amount,
                    reference_id=(
                        f"REFUND-PAYMENT-{locked_payment.pk}"
                    ),
                    description=(
                        description
                        or "بازگشت وجه پرداخت"
                    ),
                )
            )

            if not success:
                return (
                    False,
                    message,
                    locked_payment,
                )

            if amount == locked_payment.amount:

                locked_payment.status = (
                    PaymentStatusType.REFUNDED.value
                )

                locked_payment.save(
                    update_fields=[
                        "status",
                        "updated_date",
                    ]
                )

            return (
                True,
                "مبلغ با موفقیت به کیف پول بازگردانده شد",
                locked_payment,
            )