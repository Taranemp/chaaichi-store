from decimal import Decimal

from django.db import transaction

from .models import (
    Wallet,
    WalletTransaction,
    WalletTransactionStatus,
    WalletTransactionType,
)


class WalletService:

    @staticmethod
    def get_or_create_wallet(user):
        wallet, created = Wallet.objects.get_or_create(
            user=user
        )
        return wallet

    @staticmethod
    def deposit(
        user,
        amount,
        reference_id=None,
        description="",
    ):
        """
        Add money to user's wallet.

        This method should only be called after
        the external payment has been successfully verified.
        """

        amount = Decimal(amount)

        if amount <= 0:
            return False, "مبلغ باید بیشتر از صفر باشد", None

        with transaction.atomic():

            wallet = (
                Wallet.objects
                .select_for_update()
                .get(user=user)
            )

            wallet.balance += amount
            wallet.save(
                update_fields=[
                    "balance",
                    "updated_date",
                ]
            )

            wallet_transaction = WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=(
                    WalletTransactionType.DEPOSIT.value
                ),
                status=(
                    WalletTransactionStatus.SUCCESS.value
                ),
                reference_id=reference_id,
                description=description or "شارژ کیف پول",
            )

        return (
            True,
            "کیف پول با موفقیت شارژ شد",
            wallet_transaction,
        )

    @staticmethod
    def pay(
        user,
        amount,
        reference_id=None,
        description="",
    ):
        """
        Pay an order using wallet balance.
        """

        amount = Decimal(amount)

        if amount <= 0:
            return False, "مبلغ باید بیشتر از صفر باشد", None

        with transaction.atomic():

            wallet = (
                Wallet.objects
                .select_for_update()
                .get(user=user)
            )

            if wallet.balance < amount:
                return (
                    False,
                    "موجودی کیف پول کافی نیست",
                    None,
                )

            wallet.balance -= amount

            wallet.save(
                update_fields=[
                    "balance",
                    "updated_date",
                ]
            )

            wallet_transaction = WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=(
                    WalletTransactionType.PURCHASE.value
                ),
                status=(
                    WalletTransactionStatus.SUCCESS.value
                ),
                reference_id=reference_id,
                description=description or "پرداخت سفارش",
            )

        return (
            True,
            "پرداخت با کیف پول موفق بود",
            wallet_transaction,
        )

    @staticmethod
    def refund(
        user,
        amount,
        reference_id=None,
        description="",
    ):
        """
        Return money to user's wallet.
        """

        amount = Decimal(amount)

        if amount <= 0:
            return False, "مبلغ باید بیشتر از صفر باشد", None

        with transaction.atomic():

            wallet = (
                Wallet.objects
                .select_for_update()
                .get(user=user)
            )

            wallet.balance += amount

            wallet.save(
                update_fields=[
                    "balance",
                    "updated_date",
                ]
            )

            wallet_transaction = WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=(
                    WalletTransactionType.REFUND.value
                ),
                status=(
                    WalletTransactionStatus.SUCCESS.value
                ),
                reference_id=reference_id,
                description=description or "بازگشت وجه",
            )

        return (
            True,
            "مبلغ با موفقیت به کیف پول بازگردانده شد",
            wallet_transaction,
        )