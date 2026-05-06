from django.test import TestCase

from .models import ServiceCategory, ServiceEntry


class ServiceEntrySlugTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name="Banks", slug="banks")

    def test_generates_unique_slugs(self):
        first = ServiceEntry.objects.create(
            category=self.category,
            name="Campus Bank",
            description="Short summary",
            address="1 University Road",
            verified=True,
        )
        second = ServiceEntry.objects.create(
            category=self.category,
            name="Campus Bank",
            description="Short summary",
            address="2 University Road",
            verified=True,
        )

        self.assertEqual(first.slug, "campus-bank")
        self.assertEqual(second.slug, "campus-bank-2")

    def test_retrieves_entry_by_slug(self):
        entry = ServiceEntry.objects.create(
            category=self.category,
            name="Campus Clinic",
            description="Short summary",
            detail_description="## Services\n\n- Walk-ins",
            address="3 University Road",
            verified=True,
        )

        response = self.client.get(f"/api/v1/directory/entries/{entry.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["slug"], entry.slug)
        self.assertEqual(response.data["detail_description"], entry.detail_description)

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/api/v1/directory/entries/missing-entry/")

        self.assertEqual(response.status_code, 404)
