import json

import requests
from django.conf import settings


def get_protocol():
    return (
        "https"
        if getattr(settings, "SECURE_SSL_REDIRECT", False)
        else "http"
    )


class ZarinPalSandbox:

    PAYMENT_REQUEST_URL = (
        "https://sandbox.zarinpal.com/pg/rest/WebGate/"
        "PaymentRequest.json"
    )

    PAYMENT_VERIFY_URL = (
        "https://sandbox.zarinpal.com/pg/rest/WebGate/"
        "PaymentVerification.json"
    )

    PAYMENT_PAGE_URL = (
        "https://sandbox.zarinpal.com/pg/StartPay/"
    )

    def __init__(self, merchant_id=None):
        self.merchant_id = (
            merchant_id
            or getattr(settings, "MERCHANT_ID", None)
        )

        if not self.merchant_id:
            raise ValueError(
                "MERCHANT_ID is not configured in settings.py"
            )

    def get_callback_url(self):
        return (
            f"{get_protocol()}"
            f"://127.0.0.1:8000"
            f"/payment/verify/"
        )

    def payment_request(
        self,
        amount,
        description="پرداخت فروشگاه چایی چی",
    ):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": int(amount),
            "CallbackURL": self.get_callback_url(),
            "Description": description,
        }

        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.PAYMENT_REQUEST_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def payment_verify(self, amount, authority):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": int(amount),
            "Authority": authority,
        }

        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.PAYMENT_VERIFY_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def generate_payment_url(self, authority):
        return f"{self.PAYMENT_PAGE_URL}{authority}"