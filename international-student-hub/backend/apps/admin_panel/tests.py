from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from apps.bot.models import BotFAQ
from apps.checklist.models import ChecklistCategory


class AdminPanelAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pass12345")
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass12345"
        )

    def test_profile_includes_superuser_flags(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get("/api/v1/auth/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_staff"])
        self.assertTrue(response.data["is_superuser"])

    def test_normal_user_cannot_access_admin_api(self):
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/v1/admin-panel/users/")

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_list_and_create_model(self):
        self.client.force_authenticate(self.admin)
        ChecklistCategory.objects.create(name="Arrival")

        list_response = self.client.get("/api/v1/admin-panel/checklist-categories/")
        create_response = self.client.post(
            "/api/v1/admin-panel/checklist-categories/",
            {"name": "Banking", "description": "Money setup", "order": 2, "icon": ""},
            format="json",
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(ChecklistCategory.objects.count(), 2)

    def test_superuser_can_update_and_delete_model(self):
        self.client.force_authenticate(self.admin)
        faq = BotFAQ.objects.create(trigger_keyword="arc", response_text="Bring passport.")

        update_response = self.client.patch(
            f"/api/v1/admin-panel/bot-faqs/{faq.id}/",
            {"active": False},
            format="json",
        )
        delete_response = self.client.delete(f"/api/v1/admin-panel/bot-faqs/{faq.id}/")

        self.assertEqual(update_response.status_code, 200)
        self.assertFalse(update_response.data["active"])
        self.assertEqual(delete_response.status_code, 204)
