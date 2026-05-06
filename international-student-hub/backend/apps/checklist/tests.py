from django.test import TestCase

from .models import ChecklistCategory, ChecklistItem


class ChecklistItemSlugTests(TestCase):
    def setUp(self):
        self.category = ChecklistCategory.objects.create(name="Arrival")

    def test_generates_unique_slugs(self):
        first = ChecklistItem.objects.create(
            category=self.category,
            title="Open a Bank Account",
            description="Short summary",
        )
        second = ChecklistItem.objects.create(
            category=self.category,
            title="Open a Bank Account",
            description="Short summary",
        )

        self.assertEqual(first.slug, "open-a-bank-account")
        self.assertEqual(second.slug, "open-a-bank-account-2")

    def test_retrieves_item_by_slug(self):
        item = ChecklistItem.objects.create(
            category=self.category,
            title="Apply for ARC",
            description="Short summary",
            detail_description="## Steps\n\n- Bring your passport",
        )

        response = self.client.get(f"/api/v1/checklist/items/{item.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["slug"], item.slug)
        self.assertEqual(response.data["detail_description"], item.detail_description)

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/api/v1/checklist/items/missing-item/")

        self.assertEqual(response.status_code, 404)
