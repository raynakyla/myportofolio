"""Regression coverage from the final Tugas 3 audit (isolated test database)."""

import uuid
from datetime import datetime, timezone

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from main.forms import ExperienceForm
from main.models import Experience

from django.contrib.auth.models import User

class ExperienceRegressionTests(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Existing chapter",
            description="Original details",
            category="career",
            started_at=datetime(2024, 1, 1, 9, tzinfo=timezone.utc),
        )

        self.superuser = User.objects.create_superuser(
            username="regression_admin",
            email="regressionadmin@example.com",
            password="testpass123",
        )

        self.client.force_login(self.superuser)

        self.add_url = reverse("main:create_experience")
        self.edit_url = reverse("main:update_experience", args=[self.experience.pk])
        self.delete_url = reverse("main:delete_experience", args=[self.experience.pk])
        self.payload = {
            "title": "Past experience",
            "description": "Completed before it was recorded",
            "category": "community",
            "thumbnail": "",
            "started_at": "2023-01-01T09:00",
            "ended_at": "2023-06-01T17:00",
        }

    def test_empty_post_shows_errors_and_preserves_database(self):
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.client.post(url, {})
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], "title", "This field is required.")
                self.assertContains(response, "This field is required.")
                self.assertEqual(Experience.objects.count(), 1)
                self.experience.refresh_from_db()
                self.assertEqual(self.experience.description, "Original details")

    def test_completed_historical_experience_can_be_created_and_edited(self):
        response = self.client.post(self.add_url, self.payload)
        self.assertRedirects(response, reverse("main:show_experience"))
        created = Experience.objects.get(title=self.payload["title"])
        created.full_clean()
        self.assertEqual(created.started_at.year, 2023)
        self.assertEqual(created.ended_at.month, 6)
        url = reverse("main:update_experience", args=[created.pk])
        form_page = self.client.get(url)
        self.assertContains(form_page, 'value="2023-01-01T09:00"')
        self.assertContains(form_page, 'value="2023-06-01T17:00"')
        response = self.client.post(url, {**self.payload, "title": "Updated past experience"})
        self.assertRedirects(response, reverse("main:show_experience"))
        created.refresh_from_db()
        self.assertEqual(created.title, "Updated past experience")
        self.assertEqual(Experience.objects.count(), 2)

    def test_reversed_dates_are_rejected_on_create_and_update(self):
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.client.post(url, {**self.payload, "ended_at": "2022-01-01T09:00"})
                self.assertEqual(response.status_code, 200)
                self.assertIn("ended_at", response.context["form"].errors)
                self.assertContains(response, self.payload["description"])
                self.assertEqual(Experience.objects.count(), 1)
                self.experience.refresh_from_db()
                self.assertEqual(self.experience.title, "Existing chapter")
                self.assertIsNone(self.experience.ended_at)

    def test_same_start_and_end_are_allowed(self):
        form = ExperienceForm({**self.payload, "ended_at": self.payload["started_at"]})
        self.assertTrue(form.is_valid(), form.errors)

    def test_unknown_dates_do_not_invent_a_start_time(self):
        response = self.client.post(self.add_url, {**self.payload, "started_at": "", "ended_at": ""})
        self.assertRedirects(response, reverse("main:show_experience"))
        created = Experience.objects.get(title=self.payload["title"])
        self.assertIsNone(created.started_at)
        self.assertTrue(created.is_ongoing)
        page = self.client.get(reverse("main:show_experience"))
        self.assertContains(page, "Start date not specified")

    def test_invalid_url_category_and_datetime_do_not_save(self):
        invalid_fields = {
            "thumbnail": "javascript:alert(1)",
            "category": "not-a-category",
            "started_at": "not-a-date",
            "ended_at": "not-a-date",
        }
        for field, value in invalid_fields.items():
            with self.subTest(field=field):
                response = self.client.post(self.add_url, {**self.payload, field: value})
                self.assertIn(field, response.context["form"].errors)
                self.assertEqual(Experience.objects.count(), 1)

    def test_all_editable_fields_are_in_form(self):
        editable = {field.name for field in Experience._meta.fields if field.editable}
        self.assertEqual(set(ExperienceForm().fields), editable)

    def test_csrf_blocks_each_mutation_and_accepts_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.superuser)
        
        for url in (self.add_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                self.assertEqual(client.post(url, self.payload).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Existing chapter")

        client.get(self.add_url)
        token = client.cookies["csrftoken"].value
        for url in (self.add_url, self.edit_url, self.delete_url):
            with self.subTest(valid_token_url=url):
                response = client.post(url, {**self.payload, "csrfmiddlewaretoken": token})
                self.assertRedirects(response, reverse("main:show_experience"))
                self.assertTrue(any(message.level_tag == "success" for message in get_messages(response.wsgi_request)))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertEqual(Experience.objects.count(), 1)

    def test_missing_and_malformed_ids_never_create_data(self):
        for identifier in (uuid.uuid4(), "invalid-uuid"):
            for action in ("edit", "delete"):
                with self.subTest(identifier=identifier, action=action):
                    response = self.client.post(f"/experience/{identifier}/{action}/", self.payload)
                    self.assertEqual(response.status_code, 404)
        self.assertEqual(Experience.objects.count(), 1)

    def test_json_and_groups_keep_all_categories_and_date_order(self):
        recent = Experience.objects.create(
            title="Recent career", description="Recent", category="career",
            started_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        for category, label in Experience.EXPERIENCE_CHOICES:
            Experience.objects.create(title=label, description="Unknown start", category=category)
        response = self.client.get(reverse("main:get_experiences_json"))
        payload = response.json()
        self.assertEqual(len(payload), 8)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual({row["fields"]["category"] for row in payload}, {key for key, _ in Experience.EXPERIENCE_CHOICES})
        self.assertTrue(any(row["fields"]["started_at"] is None for row in payload))
        page = self.client.get(reverse("main:show_experience"))
        groups = page.context["experience_groups"]
        self.assertEqual([group["key"] for group in groups], [key for key, _ in Experience.EXPERIENCE_CHOICES])
        self.assertEqual([item.pk for item in groups[0]["items"][:2]], [recent.pk, self.experience.pk])
        self.assertEqual(sum(len(group["items"]) for group in groups), 8)

    def test_empty_json_is_an_array(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(response.json(), [])

    def test_forms_inherit_shared_layout_and_expose_help_text(self):
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, "base.html")
                self.assertContains(response, 'id="id_started_at_helptext"')
                self.assertContains(response, 'aria-describedby="id_started_at_helptext"')

