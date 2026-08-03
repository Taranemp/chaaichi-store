# order/views.py

from django.views.generic import FormView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db import transaction
import json

from cart.cart import CartSession

from payment.models import (
    Wallet,
    Transaction,
    TransactionStatusType,
    TransactionType
)

from .models import (
    Order,
    OrderStatusType,
    OrderItem,
    UserAddress,
    Coupon
)

from .forms import (
    CheckoutForm,
    CITIES_BY_STATE
)



class CheckoutView(LoginRequiredMixin, FormView):

    template_name = "order/checkout.html"

    form_class = CheckoutForm

    success_url = reverse_lazy(
        "order:success"
    )


    # -------------------------
    # Cart Calculation
    # -------------------------

    def get_cart_data(self):

        cart = CartSession(
            self.request
        )


        summary = cart.get_price_summary()


        items_total = summary["original_total"]

        products_discount = summary["discount_total"]

        cart_total = summary["final_total"]



        shipping_cost = 36000


        if cart_total >= 500000:

            shipping_cost = 0



        return {

            "cart": cart,

            "cart_items": cart.get_items(),


            "items_total": items_total,


            "products_discount": products_discount,


            "cart_total": cart_total,


            "shipping_cost": shipping_cost,


            "coupon_discount": 0,


            "final_price":
                cart_total + shipping_cost,

        }



    # -------------------------
    # Form kwargs
    # -------------------------

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()


        cart_data = self.get_cart_data()


        kwargs["user"] = self.request.user


        kwargs["cart_total"] = (
            cart_data["final_price"]
        )


        return kwargs



    # -------------------------
    # Template Context
    # -------------------------

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        cart_data = self.get_cart_data()


        wallet, _ = Wallet.objects.get_or_create(
            user=self.request.user
        )


        context.update({

            "addresses":
                UserAddress.objects.filter(
                    user=self.request.user
                ),


            "cart_items":
                cart_data["cart_items"],


            "items_total":
                cart_data["items_total"],


            "products_discount":
                cart_data["products_discount"],


            "cart_total":
                cart_data["cart_total"],


            "shipping_cost":
                cart_data["shipping_cost"],


            "coupon_discount":
                cart_data["coupon_discount"],


            "final_price":
                cart_data["final_price"],


            "wallet_balance":
                wallet.balance,


            "cities_json":
                json.dumps(
                    CITIES_BY_STATE,
                    ensure_ascii=False
                )

        })


        return context



    # -------------------------
    # Create Order
    # -------------------------

    def form_valid(self, form):


        cart_data = self.get_cart_data()


        cart = cart_data["cart"]

        cart_items = cart_data["cart_items"]


        if not cart_items:

            messages.error(
                self.request,
                "سبد خرید شما خالی است."
            )

            return redirect(
                "cart:summary"
            )



        coupon = form.cleaned_data.get(
            "coupon_code"
        )


        coupon_discount = 0



        # Coupon Apply

        if coupon:


            coupon_result = coupon.apply(

                self.request.user,

                cart_data["cart_total"]

            )


            if coupon_result[0]:

                new_price, _ = coupon_result


                coupon_discount = (
                    cart_data["cart_total"]
                    -
                    new_price
                )


                cart_data["final_price"] = (
                    new_price
                    +
                    cart_data["shipping_cost"]
                )



        final_price = (
            cart_data["final_price"]
        )



        wallet, _ = Wallet.objects.get_or_create(
            user=self.request.user
        )



        if wallet.balance < final_price:

            messages.error(
                self.request,
                "موجودی کیف پول کافی نیست."
            )

            return redirect(
                "payment:wallet"
            )



        selected_address = form.cleaned_data.get(
            "selected_address"
        )



        with transaction.atomic():



            wallet.deduct(
                final_price
            )



            transaction_obj = Transaction.objects.create(

                user=self.request.user,

                amount=final_price,

                status=
                TransactionStatusType.SUCCESS.value,

                transaction_type=
                TransactionType.PURCHASE.value,

                description=
                "خرید از فروشگاه Chaai Chi"

            )



            order = Order.objects.create(

                user=self.request.user,


                transaction=transaction_obj,


                coupon=coupon,


                receiver_name=(

                    selected_address.receiver_name

                    if selected_address

                    else form.cleaned_data.get(
                        "receiver_name"
                    )

                ),


                receiver_phone=(

                    selected_address.receiver_phone

                    if selected_address

                    else form.cleaned_data.get(
                        "receiver_phone"
                    )

                ),


                address=(

                    selected_address.address

                    if selected_address

                    else form.cleaned_data.get(
                        "address"
                    )

                ),


                state=(

                    selected_address.state

                    if selected_address

                    else form.cleaned_data.get(
                        "state"
                    )

                ),


                city=(

                    selected_address.city

                    if selected_address

                    else form.cleaned_data.get(
                        "city"
                    )

                ),


                zip_code=(

                    selected_address.zip_code

                    if selected_address

                    else form.cleaned_data.get(
                        "zip_code"
                    )

                ),



                items_total=
                cart_data["items_total"],



                products_discount=
                cart_data["products_discount"],



                coupon_discount=
                coupon_discount,



                shipping_cost=
                cart_data["shipping_cost"],



                total_price=
                final_price,



                status=
                OrderStatusType.PENDING.value

            )



            # Order Items

            for item in cart_items:


                product = item.product


                OrderItem.objects.create(

                    order=order,


                    product=product,


                    product_title=
                    product.title,


                    product_slug=
                    product.slug,


                    quantity=
                    item.quantity,


                    original_price=
                    product.price,


                    discount_amount=
                    product.discount_amount,


                    unit_price=
                    product.final_price,

                )



            cart.clear()



        messages.success(

            self.request,

            f"سفارش شما با موفقیت ثبت شد. شماره سفارش: #{order.id}"

        )


        self.request.session[
            "last_order_id"
        ] = order.id



        return super().form_valid(form)





class OrderSuccessView(LoginRequiredMixin, TemplateView):

    template_name = "order/success.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        order_id = self.request.session.get(
            "last_order_id"
        )


        if order_id:

            try:

                order = Order.objects.get(

                    id=order_id,

                    user=self.request.user

                )


                context["order"] = order


                context["order_items"] = (
                    order.items
                    .select_related("product")
                    .all()
                )


            except Order.DoesNotExist:

                pass



        return context





class OrderFailedView(LoginRequiredMixin, TemplateView):

    template_name = "order/failed.html"





class OrderDetailView(LoginRequiredMixin, DetailView):

    template_name = "order/order-detail.html"

    model = Order

    context_object_name = "order"



    def get_queryset(self):

        return Order.objects.filter(
            user=self.request.user
        )