from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from order.models import Order
from order.services import OrderService

from .models import (
    Payment,
    PaymentStatusType,
    PaymentMethodType,
    PaymentPurposeType,
)
from .services import PaymentService


# =========================================================
# START GATEWAY PAYMENT
# =========================================================

class GatewayPaymentStartView(LoginRequiredMixin, View):
    """
    درخواست شروع پرداخت درگاه بانکی.
    """

    def post(self, request, *args, **kwargs):
        payment = get_object_or_404(
            Payment,
            pk=kwargs.get("pk"),
            user=request.user,
        )

        # اعتبارسنجی روش پرداخت
        if payment.method != PaymentMethodType.GATEWAY.value:
            messages.error(request, "این پرداخت از نوع درگاه نیست.")
            return redirect("dashboard:home")

        # اعتبارسنجی وضعیت پرداخت
        if payment.status != PaymentStatusType.PENDING.value:
            messages.warning(request, "این پرداخت دیگر قابل انجام نیست.")
            return redirect("dashboard:home")

        # ارسال درخواست به درگاه
        success, message, result = PaymentService.start_gateway_payment(payment)

        if not success:
            messages.error(request, message)
            return redirect("dashboard:home")

        # هدایت به لینک درگاه
        payment_url = result.get("payment_url")
        if not payment_url:
            messages.error(request, "آدرس درگاه پرداخت دریافت نشد.")
            return redirect("dashboard:home")

        return redirect(payment_url)


# =========================================================
# GATEWAY CALLBACK
# =========================================================

class GatewayPaymentCallbackView(View):
    """
    دریافت بازگشت (Callback) از درگاه پرداخت.
    """

    def get(self, request, *args, **kwargs):
        authority = request.GET.get("Authority")
        gateway_status = request.GET.get("Status")

        # اعتبارسنجی دریافت Authority
        if not authority:
            messages.error(request, "اطلاعات پرداخت از درگاه دریافت نشد.")
            return redirect("dashboard:home")

        # پیدا کردن رکورد پرداخت
        payment = (
            Payment.objects
            .select_related("user")
            .filter(authority=authority)
            .first()
        )

        if not payment:
            messages.error(request, "پرداخت موردنظر پیدا نشد.")
            return redirect("dashboard:home")

        # اگر قبلاً تأیید شده است
        if payment.status == PaymentStatusType.SUCCESS.value:
            messages.info(request, "این پرداخت قبلاً تأیید شده است.")
            return redirect(self.get_success_url(payment))

        # اگر کاربر در درگاه پرداخت را لغو کرده یا خطا رخ داده
        if gateway_status != "OK":
            PaymentService.mark_gateway_failed(payment)
            messages.warning(request, "پرداخت توسط کاربر لغو شد یا با خطا مواجه گردید.")
            return redirect(self.get_failure_url(payment))

        # استعلام و تأیید پرداخت از درگاه
        success, message, verified_payment = PaymentService.verify_gateway_payment(
            payment=payment,
            authority=authority,
        )

        if not success:
            messages.error(request, message)
            return redirect(self.get_failure_url(verified_payment or payment))

        messages.success(request, "پرداخت با موفقیت انجام شد.")
        return redirect(self.get_success_url(verified_payment))

    @staticmethod
    def get_success_url(payment):
        return reverse("payment:success", kwargs={"pk": payment.pk})

    @staticmethod
    def get_failure_url(payment):
        return reverse("payment:failed", kwargs={"pk": payment.pk})


# =========================================================
# PAYMENT SUCCESS
# =========================================================

class PaymentSuccessView(LoginRequiredMixin, View):
    """
    مدیریت نهایی‌سازی اکشن‌ها پس از پرداخت موفق.
    """

    def get(self, request, *args, **kwargs):
        payment = get_object_or_404(
            Payment,
            pk=kwargs.get("pk"),
            user=request.user,
        )

        # اطمینان از موفق بودن پرداخت
        if payment.status != PaymentStatusType.SUCCESS.value:
            return redirect("payment:failed", pk=payment.pk)

        # -------------------------------------------------
        # نهایی‌سازی سفارش در صورت پرداخت سفارش
        # -------------------------------------------------
        if payment.purpose == PaymentPurposeType.ORDER.value:
            order = Order.objects.filter(payment=payment).first()

            if not order:
                messages.error(request, "سفارش مرتبط با این پرداخت یافت نشد.")
                return redirect("dashboard:home")

            # فراخوانی OrderService جهت تغییر وضعیت، پاکسازی Cart و ثبت کوپن
            success, message, finalized_order = OrderService.finalize_order(order)

            if not success:
                messages.error(request, message)
                return redirect("dashboard:home")

            return redirect("order:success", pk=finalized_order.pk)

        # -------------------------------------------------
        # شارژ کیف پول
        # -------------------------------------------------
        if payment.purpose == PaymentPurposeType.WALLET_DEPOSIT.value:
            messages.success(request, "کیف پول شما با موفقیت شارژ شد.")
            return redirect("dashboard:home")

        messages.error(request, "هدف پرداخت نامعتبر است.")
        return redirect("dashboard:home")


# =========================================================
# PAYMENT FAILED
# =========================================================

class PaymentFailedView(LoginRequiredMixin, View):
    """
    مدیریت نمایش و هدایت پس از پرداخت ناموفق یا لغوشده.
    """

    def get(self, request, *args, **kwargs):
        payment = get_object_or_404(
            Payment,
            pk=kwargs.get("pk"),
            user=request.user,
        )

        # اگر پرداخت در واقع موفق بوده است
        if payment.status == PaymentStatusType.SUCCESS.value:
            return redirect("payment:success", pk=payment.pk)

        # اگر پرداخت مربوط به سفارش بوده
        if payment.purpose == PaymentPurposeType.ORDER.value:
            order = Order.objects.filter(payment=payment).first()
            order_id = order.pk if order else payment.pk
            return redirect("order:failed", pk=order_id)

        # اگر مربوط به شارژ کیف پول بوده
        if payment.purpose == PaymentPurposeType.WALLET_DEPOSIT.value:
            messages.error(request, "پرداخت شارژ کیف پول ناموفق بود.")
            return redirect("dashboard:home")

        messages.error(request, "هدف پرداخت نامعتبر است.")
        return redirect("dashboard:home")