from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone="09120000000",
            fullname="john doe",
            email="test@example.com",
            password="testpass123"
        )

    def test_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": "09120000000", "password": "testpass123"},
            follow=True
        )
        self.assertTrue(response.context["user"].is_authenticated)

    def test_logout(self):
        self.client.login(username="09120000000", password="testpass123")
        response = self.client.get(reverse("logout"), follow=True)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_login_url_exists(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
