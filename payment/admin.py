from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance", "created_date")
    list_filter = ("created_date",)
    search_fields = ("user__phone", "user__fullname")
    readonly_fields = ("balance",)  

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "status", "transaction_type", "created_date")
    list_filter = ("status", "transaction_type", "created_date")
    search_fields = ("user__phone", "reference_id")
    readonly_fields = ("created_date", "updated_date")