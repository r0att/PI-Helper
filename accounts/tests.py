from django.test import TestCase
from django.urls import reverse

from .models import PasswordChangeToken, User


class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="OldPassword123!",
            is_active=True,
        )

        self.client.login(
            username="testuser",
            password="OldPassword123!",
        )

    def test_change_password_page_requires_login(self):
        self.client.logout()

        response = self.client.get(
            reverse("change_password")
        )

        self.assertEqual(response.status_code, 302)

    def test_change_password_sends_confirmation(self):
        response = self.client.post(
            reverse("change_password"),
            {
                "current_password": "OldPassword123!",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/password_change_sent.html",
        )

        self.assertEqual(
            PasswordChangeToken.objects.count(),
            1,
        )

    def test_change_password_rejects_wrong_current_password(self):
        response = self.client.post(
            reverse("change_password"),
            {
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            PasswordChangeToken.objects.count(),
            0,
        )

    def test_change_password_rejects_different_passwords(self):
        response = self.client.post(
            reverse("change_password"),
            {
                "current_password": "OldPassword123!",
                "new_password": "NewPassword123!",
                "confirm_password": "DifferentPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            PasswordChangeToken.objects.count(),
            0,
        )

    def test_confirm_password_change(self):
        self.client.post(
            reverse("change_password"),
            {
                "current_password": "OldPassword123!",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!",
            },
        )

        token = PasswordChangeToken.objects.get(
            user=self.user
        )

        response = self.client.get(
            reverse(
                "confirm_password_change",
                args=[token.token],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/password_change_success.html",
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("NewPassword123!")
        )
        self.assertFalse(
            self.user.check_password("OldPassword123!")
        )

        self.assertFalse(
            PasswordChangeToken.objects.filter(
                user=self.user
            ).exists()
        )

    def test_invalid_password_change_token(self):
        import uuid

        response = self.client.get(
            reverse(
                "confirm_password_change",
                args=[uuid.uuid4()],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/password_change_invalid.html",
        )