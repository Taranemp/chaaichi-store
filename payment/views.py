from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from shop.models import Product
from order.models import Order, OrderStatusType
from .services import WalletService
from .models import Transaction




class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, product_id, quantity):
        product = get_object_or_404(Product, id=product_id, status=1)
        quantity = int(quantity)
        total_price = product.get_price() * quantity

        context = {
            "product": product,
            "quantity": quantity,
            "total_price": total_price,
            "wallet_balance": request.user.wallet.balance,
        }
        return render(request, "payment/checkout.html", context)

    def post(self, request, product_id, quantity):
        product = get_object_or_404(Product, id=product_id, status=1)
        quantity = int(quantity)
        total_price = product.get_price() * quantity

        success, message, transaction = WalletService.purchase(
            user=request.user,
            product=product,
            quantity=quantity
        )

        if success:
            order = Order.objects.create(
                user=request.user,
                transaction=transaction,
                total_amount=total_price,
                status=OrderStatusType.PENDING.value
            )
            order.items.create(
                product=product,
                quantity=quantity,
                price=product.get_price()
            )
            messages.success(request, message)
            return redirect("payment:success")
        else:
            messages.error(request, message)
            return redirect("payment:failed")


class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "payment/success.html")


class PaymentFailedView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "payment/failed.html")


class WalletView(LoginRequiredMixin, View):
    def get(self, request):
        wallet = request.user.wallet
        transactions = Transaction.objects.filter(user=request.user)[:20]

        context = {
            "wallet": wallet,
            "transactions": transactions,
        }
        return render(request, "payment/wallet.html", context)


