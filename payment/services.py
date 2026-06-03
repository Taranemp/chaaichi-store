from decimal import Decimal
from django.db import transaction as db_transaction
from .models import Wallet, Transaction, TransactionStatusType, TransactionType


class WalletService:
    
    @staticmethod
    def get_or_create_wallet(user):
        """Get or create wallet for user"""
        wallet, created = Wallet.objects.get_or_create(user=user)
        return wallet
    
    @staticmethod
    def purchase(user, product, quantity):
        """
        Purchase a product using wallet balance
        
        Flow:
        1. Check quantity > 0
        2. Check product stock >= quantity
        3. Check wallet balance >= total_price
        4. Atomic transaction (select_for_update)
        5. Deduct from wallet
        6. Create Transaction record (SUCCESS)
        7. Decrease product stock
        """
        wallet = WalletService.get_or_create_wallet(user)
        total_price = product.get_price() * quantity

        
        # 1. Invalid quantity
        if quantity <= 0:
            return False, "Invalid quantity"

        # 2. Insufficient product stock
        if product.stock < quantity:
            return False, f"Insufficient stock. Only {product.stock} available"

        # 3. Insufficient wallet balance
        if not wallet.has_sufficient_balance(total_price):
            return False, f"Insufficient wallet balance. You have {wallet.balance:,} Toman"

        # ========== Atomic transaction with row lock ==========
        with db_transaction.atomic():
            # Lock the wallet row to prevent race conditions (double spending)
            wallet = Wallet.objects.select_for_update().get(id=wallet.id)

            # Double-check balance for extra security within atomic block
            if wallet.balance < total_price:
                return False, "Insufficient balance"

            # Step 5: Deduct from wallet
            wallet.deduct(total_price)

            # Step 6: Create successful Transaction record
            transaction_obj = Transaction.objects.create(
                user=user,
                amount=total_price,
                status=TransactionStatusType.SUCCESS.value,
                transaction_type=TransactionType.PURCHASE.value,
                description=f"Purchase {quantity} x {product.title}"
            )

            # Step 7: Decrease product stock
            product.stock -= quantity
            product.save()

            return True, "Purchase successful", transaction_obj

    @staticmethod
    def deposit(user, amount):
        """Deposit money into wallet (for store management)"""
        if amount <= 0:
            return False, "Invalid amount"

        wallet = WalletService.get_or_create_wallet(user)

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(id=wallet.id)
            wallet.add(amount)

            Transaction.objects.create(
                user=user,
                amount=amount,
                status=TransactionStatusType.SUCCESS.value,
                transaction_type=TransactionType.DEPOSIT.value,
                description="Wallet deposit"
            )

            return True, "Deposit successful"