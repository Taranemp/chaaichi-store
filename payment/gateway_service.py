from django.db import transaction

from .models import (
    Payment,
    PaymentMethodType,
    PaymentStatusType,
)

from .zarinpal_client import ZarinPalSandbox


class GatewayService:
    """
    Gateway integration layer.

    Responsibilities:
        - Create gateway payment request
        - Return authority and payment URL
        - Verify gateway payment
        - Return gateway reference ID

    Business logic such as:
        - changing Payment status
        - charging wallet
        - finalizing order
        - clearing cart

    belongs to PaymentService / OrderService.
    """

    # =========================================================
    # GATEWAY CLIENT
    # =========================================================

    @staticmethod
    def get_gateway():
        return ZarinPalSandbox()

    # =========================================================
    # CREATE PAYMENT REQUEST
    # =========================================================

    @staticmethod
    def request_payment(
        amount,
        description="پرداخت فروشگاه چای چی",
    ):
        """
        Create a payment request in the gateway.

        Returns:

            {
                "success": True,
                "message": "...",
                "authority": "...",
                "payment_url": "..."
            }

        or:

            {
                "success": False,
                "message": "...",
                "authority": None,
                "payment_url": None
            }
        """

        if amount is None:
            return {
                "success": False,
                "message": "مبلغ پرداخت مشخص نشده است",
                "authority": None,
                "payment_url": None,
            }

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": "مبلغ پرداخت نامعتبر است",
                "authority": None,
                "payment_url": None,
            }

        if amount <= 0:
            return {
                "success": False,
                "message": "مبلغ پرداخت باید بیشتر از صفر باشد",
                "authority": None,
                "payment_url": None,
            }

        try:
            gateway = GatewayService.get_gateway()

            response = gateway.payment_request(
                amount=amount,
                description=description,
            )

        except Exception as exc:
            return {
                "success": False,
                "message": (
                    f"خطا در ارتباط با درگاه پرداخت: {exc}"
                ),
                "authority": None,
                "payment_url": None,
            }

        if not isinstance(response, dict):
            return {
                "success": False,
                "message": "پاسخ نامعتبر از درگاه دریافت شد",
                "authority": None,
                "payment_url": None,
            }

        authority = response.get("Authority")
        status = str(response.get("Status"))

        # ZarinPal:
        # 100 = successful request
        # 101 = already requested / successful
        if not authority or status not in ("100", "101"):
            return {
                "success": False,
                "message": (
                    response.get("Message")
                    or "خطا در ایجاد درخواست پرداخت درگاه"
                ),
                "authority": None,
                "payment_url": None,
            }

        try:
            payment_url = gateway.generate_payment_url(
                authority
            )
        except Exception as exc:
            return {
                "success": False,
                "message": (
                    f"آدرس درگاه ایجاد نشد: {exc}"
                ),
                "authority": authority,
                "payment_url": None,
            }

        if not payment_url:
            return {
                "success": False,
                "message": "آدرس درگاه پرداخت دریافت نشد",
                "authority": authority,
                "payment_url": None,
            }

        return {
            "success": True,
            "message": "درخواست پرداخت با موفقیت ایجاد شد",
            "authority": authority,
            "payment_url": payment_url,
        }

    # =========================================================
    # VERIFY PAYMENT
    # =========================================================

    @staticmethod
    def verify_payment(
        amount,
        authority,
    ):
        """
        Verify a payment with the gateway.

        This method DOES NOT modify Payment.

        It only asks the gateway whether the payment
        was successful.

        Returns:

            {
                "success": True,
                "message": "...",
                "reference_id": "..."
            }

        or:

            {
                "success": False,
                "message": "...",
                "reference_id": None
            }
        """

        if not authority:
            return {
                "success": False,
                "message": "کد Authority دریافت نشد",
                "reference_id": None,
            }

        if amount is None:
            return {
                "success": False,
                "message": "مبلغ پرداخت مشخص نشده است",
                "reference_id": None,
            }

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": "مبلغ پرداخت نامعتبر است",
                "reference_id": None,
            }

        if amount <= 0:
            return {
                "success": False,
                "message": "مبلغ پرداخت نامعتبر است",
                "reference_id": None,
            }

        try:
            gateway = GatewayService.get_gateway()

            response = gateway.payment_verify(
                amount=amount,
                authority=authority,
            )

        except Exception as exc:
            return {
                "success": False,
                "message": (
                    f"خطا در ارتباط با درگاه پرداخت: {exc}"
                ),
                "reference_id": None,
            }

        if not isinstance(response, dict):
            return {
                "success": False,
                "message": "پاسخ نامعتبر از درگاه دریافت شد",
                "reference_id": None,
            }

        status = str(response.get("Status"))

        reference_id = response.get("RefID")

        # ZarinPal:
        # 100 = successful verification
        # 101 = already verified
        if status not in ("100", "101"):
            return {
                "success": False,
                "message": (
                    response.get("Message")
                    or "پرداخت توسط درگاه تأیید نشد"
                ),
                "reference_id": None,
            }

        return {
            "success": True,
            "message": "پرداخت با موفقیت توسط درگاه تأیید شد",
            "reference_id": (
                str(reference_id)
                if reference_id is not None
                else None
            ),
        }

    # =========================================================
    # START PAYMENT FOR PAYMENT OBJECT
    # =========================================================

    @staticmethod
    def create_payment_request(payment):
        """
        Convenience method for an existing Payment object.

        This method:
            - validates Payment
            - contacts gateway
            - saves authority
            - returns payment URL

        It does NOT mark Payment as SUCCESS.
        """

        if not payment:
            return (
                False,
                "پرداخت پیدا نشد",
                None,
            )

        if payment.method != PaymentMethodType.GATEWAY.value:
            return (
                False,
                "این پرداخت مربوط به درگاه نیست",
                None,
            )

        if payment.status != PaymentStatusType.PENDING.value:
            return (
                False,
                "وضعیت پرداخت قابل ارسال به درگاه نیست",
                None,
            )

        if payment.amount <= 0:
            return (
                False,
                "مبلغ پرداخت نامعتبر است",
                None,
            )

        result = GatewayService.request_payment(
            amount=payment.amount,
            description=(
                payment.description
                or f"پرداخت سفارش #{payment.pk}"
            ),
        )

        if not result.get("success"):
            return (
                False,
                result.get(
                    "message",
                    "خطا در ایجاد درخواست پرداخت",
                ),
                None,
            )

        authority = result.get("authority")
        payment_url = result.get("payment_url")

        if not authority:
            return (
                False,
                "Authority از درگاه دریافت نشد",
                None,
            )

        if not payment_url:
            return (
                False,
                "آدرس درگاه دریافت نشد",
                None,
            )

        # Save only gateway information.
        # Payment status remains PENDING.
        payment.authority = authority

        payment.save(
            update_fields=[
                "authority",
                "updated_date",
            ]
        )

        return (
            True,
            "درخواست پرداخت با موفقیت ایجاد شد",
            {
                "payment": payment,
                "authority": authority,
                "payment_url": payment_url,
            },
        )