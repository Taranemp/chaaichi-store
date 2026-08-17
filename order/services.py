from django.db import transaction

from cart.models import Cart

from .models import Order, OrderStatusType


class OrderService:

    # =====================================================
    # FINALIZE ORDER
    # =====================================================

    @staticmethod
    @transaction.atomic
    def finalize_order(order):

        if not order:
            return (
                False,
                "سفارش پیدا نشد",
                None,
            )

        # -------------------------------------------------
        # Lock Order
        # -------------------------------------------------

        try:

            locked_order = (
                Order.objects
                .select_for_update()
                .select_related(
                    "payment",
                    "coupon",
                )
                .get(
                    pk=order.pk
                )
            )

        except Order.DoesNotExist:

            return (
                False,
                "سفارش پیدا نشد",
                None,
            )

        # -------------------------------------------------
        # Already successful
        # -------------------------------------------------

        if (
            locked_order.status
            == OrderStatusType.SUCCESS.value
        ):

            return (
                True,
                "این سفارش قبلاً نهایی شده است",
                locked_order,
            )

        # -------------------------------------------------
        # Failed order
        # -------------------------------------------------

        if (
            locked_order.status
            == OrderStatusType.FAILED.value
        ):

            return (
                False,
                "این سفارش ناموفق است و قابل نهایی‌سازی نیست",
                locked_order,
            )

        # -------------------------------------------------
        # Payment must exist
        # -------------------------------------------------

        if not locked_order.payment:

            return (
                False,
                "برای این سفارش پرداختی ثبت نشده است",
                locked_order,
            )

        # -------------------------------------------------
        # Payment must be successful
        # -------------------------------------------------

        if not locked_order.payment.is_successful:

            return (
                False,
                "پرداخت سفارش موفق نشده است",
                locked_order,
            )

        # =================================================
        # FINALIZE ORDER
        # =================================================

        locked_order.status = (
            OrderStatusType.SUCCESS.value
        )

        locked_order.save(
            update_fields=[
                "status",
                "updated_date",
            ]
        )

        # =================================================
        # COUPON USAGE
        # =================================================

        if locked_order.coupon:

            coupon = locked_order.coupon

            if not coupon.used_by.filter(
                pk=locked_order.user_id
            ).exists():

                coupon.used_by.add(
                    locked_order.user_id
                )

        # =================================================
        # CLEAR CART
        # =================================================

        cart = (
            Cart.objects
            .filter(
                user=locked_order.user
            )
            .first()
        )

        if cart:

            cart.items.all().delete()

        # =================================================
        # SUCCESS
        # =================================================

        return (
            True,
            "سفارش با موفقیت نهایی شد",
            locked_order,
        )