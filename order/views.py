import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, DetailView

from cart.cart import CartSession

from payment.models import (
    PaymentMethodType,
    PaymentPurposeType,
)
from payment.services import PaymentService

from .models import (
    Order,
    OrderStatusType,
    OrderItem,
    UserAddress,
)
from .forms import CheckoutForm, CITIES_BY_STATE
from .services import OrderService


# =========================================================
# CHECKOUT VIEW
# =========================================================

class CheckoutView(LoginRequiredMixin, FormView):

    template_name = "order/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("order:success")

    # =========================================================
    # CART DATA
    # =========================================================

    def get_cart_data(self):
        cart = CartSession(self.request)
        summary = cart.get_price_summary()

        items_total = Decimal(str(summary["original_total"]))
        products_discount = Decimal(str(summary["discount_total"]))
        cart_total = Decimal(str(summary["final_total"]))

        shipping_cost = Decimal("36000")
        if cart_total >= Decimal("500000"):
            shipping_cost = Decimal("0")

        final_price = cart_total + shipping_cost

        return {
            "cart": cart,
            "cart_items": cart.get_items(),
            "items_total": items_total,
            "products_discount": products_discount,
            "cart_total": cart_total,
            "shipping_cost": shipping_cost,
            "coupon_discount": Decimal("0"),
            "final_price": final_price,
        }

    # =========================================================
    # FORM KWARGS
    # =========================================================

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        cart_data = self.get_cart_data()

        kwargs["user"] = self.request.user
        kwargs["cart_total"] = cart_data["final_price"]
        return kwargs

    # =========================================================
    # CONTEXT
    # =========================================================

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_data = self.get_cart_data()

        context.update({
            "addresses": UserAddress.objects.filter(user=self.request.user),
            "cart_items": cart_data["cart_items"],
            "items_total": cart_data["items_total"],
            "products_discount": cart_data["products_discount"],
            "cart_total": cart_data["cart_total"],
            "shipping_cost": cart_data["shipping_cost"],
            "coupon_discount": cart_data["coupon_discount"],
            "final_price": cart_data["final_price"],
            "cities_json": json.dumps(CITIES_BY_STATE, ensure_ascii=False),
        })

        return context

    # =========================================================
    # CREATE ORDER + PAYMENT
    # =========================================================

    def form_valid(self, form):
        cart_data = self.get_cart_data()
        cart = cart_data["cart"]
        cart_items = cart_data["cart_items"]

        # -----------------------------------------------------
        # Empty cart check
        # -----------------------------------------------------
        if not cart_items:
            messages.error(self.request, "سبد خرید شما خالی است.")
            return redirect("cart:summary")

        # -----------------------------------------------------
        # Selected address check
        # -----------------------------------------------------
        selected_address = form.cleaned_data.get("selected_address")
        if not selected_address:
            messages.error(self.request, "لطفاً یک آدرس معتبر انتخاب کنید.")
            return self.form_invalid(form)

        # -----------------------------------------------------
        # Coupon validation
        # -----------------------------------------------------
        coupon = form.cleaned_data.get("coupon_code")
        coupon_discount = Decimal("0")
        cart_total = Decimal(cart_data["cart_total"])
        final_cart_total = cart_total

        if coupon:
            valid, message = coupon.is_valid(
                user=self.request.user,
                total_amount=cart_total
            )

            if not valid:
                form.add_error("coupon_code", message)
                return self.form_invalid(form)

            coupon_discount = (
                cart_total * Decimal(coupon.discount_percent) / Decimal("100")
            ).quantize(Decimal("1"))

            final_cart_total = cart_total - coupon_discount

        # -----------------------------------------------------
        # Shipping and final price
        # -----------------------------------------------------
        shipping_cost = Decimal(cart_data["shipping_cost"])
        final_price = final_cart_total + shipping_cost

        # -----------------------------------------------------
        # Payment method check
        # -----------------------------------------------------
        payment_method = self.request.POST.get("payment_method")

        if payment_method == "wallet":
            payment_method_value = PaymentMethodType.WALLET.value
        elif payment_method == "zarinpal":
            payment_method_value = PaymentMethodType.GATEWAY.value
        else:
            messages.error(self.request, "روش پرداخت نامعتبر است.")
            return self.form_invalid(form)

        # =====================================================
        # DATABASE TRANSACTION
        # =====================================================
        try:
            with transaction.atomic():
                # -------------------------------------------------
                # Create Payment
                # -------------------------------------------------
                success, message, payment = PaymentService.create_payment(
                    user=self.request.user,
                    amount=final_price,
                    method=payment_method_value,
                    purpose=PaymentPurposeType.ORDER.value,
                    description="پرداخت سفارش از فروشگاه Chaai Chi",
                )

                if not success:
                    raise ValueError(message)

                # -------------------------------------------------
                # Create Order
                # -------------------------------------------------
                order = Order.objects.create(
                    user=self.request.user,
                    payment=payment,
                    coupon=coupon,
                    receiver_name=selected_address.receiver_name,
                    receiver_phone=selected_address.receiver_phone,
                    address=selected_address.address,
                    state=selected_address.state,
                    city=selected_address.city,
                    zip_code=selected_address.zip_code,
                    items_total=cart_data["items_total"],
                    products_discount=cart_data["products_discount"],
                    coupon_discount=coupon_discount,
                    shipping_cost=shipping_cost,
                    total_price=final_price,
                    status=OrderStatusType.PENDING.value,
                )

                # -------------------------------------------------
                # Create Order Items
                # -------------------------------------------------
                for item in cart_items:
                    product = item.product
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_title=product.title,
                        product_slug=product.slug,
                        quantity=item.quantity,
                        original_price=product.price,
                        discount_amount=product.discount_amount,
                        unit_price=product.final_price,
                    )

        except Exception as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

        # =====================================================
        # WALLET PAYMENT
        # =====================================================
        if payment_method_value == PaymentMethodType.WALLET.value:
            success, message, payment = PaymentService.pay_with_wallet(payment)

            if not success:
                order.status = OrderStatusType.FAILED.value
                order.save(update_fields=["status", "updated_date"])
                messages.error(self.request, message)
                return redirect("order:failed", pk=order.pk)

            # -------------------------------------------------
            # Finalize order
            # -------------------------------------------------
            success, message, order = OrderService.finalize_order(order)

            if not success:
                messages.error(self.request, message)
                return redirect("order:failed", pk=order.pk)

            self.request.session["last_order_id"] = order.id
            messages.success(self.request, "سفارش شما با موفقیت ثبت شد.")
            return redirect("order:success", pk=order.pk)

        # =====================================================
        # GATEWAY PAYMENT
        # =====================================================
        success, message, result = PaymentService.start_gateway_payment(payment)

        if not success:
            order.status = OrderStatusType.FAILED.value
            order.save(update_fields=["status", "updated_date"])
            messages.error(self.request, message)
            return redirect("order:failed", pk=order.pk)

        # Save order info for callback tracking
        self.request.session["pending_order_id"] = order.id
        self.request.session["pending_payment_id"] = payment.id

        # Extract payment url from gateway response
        payment_url = result.get("payment_url") if isinstance(result, dict) else result

        # -----------------------------------------------------
        # Redirect to Gateway
        # -----------------------------------------------------
        return redirect(payment_url)


# =========================================================
# ORDER SUCCESS
# =========================================================

class OrderSuccessView(LoginRequiredMixin, DetailView):

    template_name = "order/success.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_items"] = self.object.items.all()
        return context


# =========================================================
# ORDER FAILED
# =========================================================

class OrderFailedView(LoginRequiredMixin, DetailView):

    template_name = "order/failed.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product")
        )


# =========================================================
# ORDER DETAIL
# =========================================================

class OrderDetailView(LoginRequiredMixin, DetailView):

    template_name = "order/order-detail.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product")
        )