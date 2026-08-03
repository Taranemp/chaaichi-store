# order/views.py
from django.views.generic import FormView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db import transaction
import json

from cart.cart import CartSession
from payment.models import Wallet, Transaction, TransactionStatusType, TransactionType
from .models import Order, OrderStatusType, OrderItem, UserAddress
from .forms import CheckoutForm, OrderCreateForm, CITIES_BY_STATE


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = "order/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("order:success")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        cart = CartSession(self.request)
        kwargs['user'] = self.request.user
        kwargs['cart_total'] = cart.get_total_price()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartSession(self.request)
        
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        
        context["addresses"] = UserAddress.objects.filter(user=self.request.user)
        context["cart_items"] = cart.get_items()
        context["cart_total"] = cart.get_total_price()
        context["wallet_balance"] = wallet.balance
        context["cities_json"] = json.dumps(CITIES_BY_STATE, ensure_ascii=False)
        
        return context

    def form_valid(self, form):
        cart = CartSession(self.request)
        cart_items = cart.get_items()
        
        if not cart_items:
            messages.error(self.request, "سبد خرید شما خالی است.")
            return redirect("cart:summary")
        
        total_price = cart.get_total_price()
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        
        if wallet.balance < total_price:
            messages.error(self.request, f"موجودی کیف پول شما کافی نیست. موجودی: {wallet.balance:,} تومان")
            return redirect("payment:wallet")
        
        coupon = form.cleaned_data.get('coupon_code')
        final_price = total_price
        
        if coupon:
            discount_amount = total_price * (coupon.discount_percent / 100)
            final_price = round(total_price - discount_amount)
            coupon.used_by.add(self.request.user)
        
        selected_address = form.cleaned_data.get('selected_address')
        
        with transaction.atomic():
            wallet.deduct(final_price)
            
            transaction_obj = Transaction.objects.create(
                user=self.request.user,
                amount=final_price,
                status=TransactionStatusType.SUCCESS.value,
                transaction_type=TransactionType.PURCHASE.value,
                description=f"خرید از فروشگاه - سفارش در حال ایجاد"
            )
            
            order = Order.objects.create(
                user=self.request.user,
                transaction=transaction_obj,
                address=selected_address.address if selected_address else form.cleaned_data.get('address'),
                state=selected_address.state if selected_address else form.cleaned_data.get('state'),
                city=selected_address.city if selected_address else form.cleaned_data.get('city'),
                zip_code=selected_address.zip_code if selected_address else form.cleaned_data.get('zip_code'),
                total_price=final_price,
                coupon=coupon,
                status=OrderStatusType.PENDING.value
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.get_price()
                )
            
            cart.clear()
        
        messages.success(self.request, f"سفارش شما با موفقیت ثبت شد. شماره سفارش: #{order.id}")
        self.request.session['last_order_id'] = order.id
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "مشکلی در فرم وجود دارد. لطفاً دوباره تلاش کنید.")
        return super().form_invalid(form)


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "order/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('last_order_id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=self.request.user)
                context["order"] = order
                context["order_items"] = order.items.select_related('product').all()
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
        return Order.objects.filter(user=self.request.user)