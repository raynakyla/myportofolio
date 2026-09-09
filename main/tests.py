from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

# Create your tests here.

from main.models import Experience


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Presales Engineer Intern",
            description=(
                "Supported IT infrastructure presales through product research, "
                "BOQ preparation, requirement analysis, and technical solution support."
            ),
            category="internship",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main.html")

        self.assertNotContains(
            response,
            self.experience.title
        )

        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"'
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(
            str(self.experience),
            "Presales Engineer Intern"
        )

        self.assertEqual(
            self.experience.category,
            "internship"
        )

        self.assertTrue(
            self.experience.is_ongoing
        )

    def test_experience_page(self):
        response = self.client.get(
            reverse("main:show_experience")
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "experience.html"
        )

        self.assertContains(
            response,
            self.experience.title
        )

        self.assertContains(
            response,
            self.experience.description
        )

        self.assertContains(
            response,
            "Internship"
        )

        self.assertContains(
            response,
            "on-going"
        )

        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"'
        )

    def test_empty_experience_page(self):
        Experience.objects.all().delete()

        response = self.client.get(
            reverse("main:show_experience")
        )

        self.assertContains(
            response,
            "Belum ada pengalaman yang ditambahkan."
        )

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        response = self.client.get(
            reverse("main:show_experience")
        )

        self.assertFalse(
            self.experience.is_ongoing
        )

        self.assertContains(
            response,
            "finished"
        )

        self.assertNotContains(
            response,
            "Sedang berlangsung"
        )