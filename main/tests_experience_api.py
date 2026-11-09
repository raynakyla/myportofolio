"""DRF API coverage for the Experience portfolio section."""

import uuid
from datetime import datetime, timezone

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class ExperienceAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ordinary = User.objects.create_user(
            username="experience_reader",
            email="reader@example.com",
            password="testpass123",
        )
        cls.editor = User.objects.create_user(
            username="experience_editor",
            password="testpass123",
        )
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.owner = User.objects.create_superuser(
            username="experience_owner",
            email="owner@example.com",
            password="testpass123",
        )
        cls.career = Experience.objects.create(
            title="Career Design",
            description="Built a design system",
            category="career",
            thumbnail="https://example.com/career.png",
            started_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ended_at=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )
        cls.community = Experience.objects.create(
            title="Community Festival",
            description="Coordinated volunteers",
            category="community",
            thumbnail=None,
            started_at=None,
            ended_at=None,
        )

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.career.pk])
        self.star_url = reverse("api:experience-star", args=[self.career.pk])
        self.payload = {
            "title": "New chapter",
            "description": "Learned and contributed",
            "category": "organizations",
            "thumbnail": "https://example.com/chapter.png",
            "started_at": "2025-01-01T09:00:00Z",
            "ended_at": "2025-06-01T09:00:00Z",
        }

    def assert_original_data_unchanged(self):
        self.assertEqual(Experience.objects.count(), 2)
        self.career.refresh_from_db()
        self.community.refresh_from_db()
        self.assertEqual(self.career.title, "Career Design")
        self.assertEqual(self.career.description, "Built a design system")
        self.assertTrue(Experience.objects.filter(pk=self.community.pk).exists())

    def test_public_list_and_detail_have_only_expected_fields(self):
        listing = self.client.get(self.list_url)
        detail = self.client.get(self.detail_url)

        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 2)
        expected_fields = {
            "id", "title", "description", "category", "thumbnail",
            "started_at", "ended_at", "star_count", "is_starred",
        }
        for item in (*listing.data, detail.data):
            self.assertEqual(set(item), expected_fields)
            self.assertEqual(item["star_count"], 0)
            self.assertFalse(item["is_starred"])
            for private_field in ("starred_by", "username", "email", "password"):
                self.assertNotIn(private_field, item)
        self.assertEqual(detail.data["id"], str(self.career.pk))
        for response in (listing, detail):
            body = response.content.decode()
            self.assertNotIn(self.ordinary.username, body)
            self.assertNotIn(self.owner.email, body)
            self.assertNotIn("testpass123", body)

    def test_list_order_and_case_insensitive_trimmed_title_search(self):
        recent = Experience.objects.create(
            title="Internship Lab",
            description="Recent work",
            category="career",
            started_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )

        full = self.client.get(self.list_url)
        blank = self.client.get(self.list_url, {"title": "   "})
        matched = self.client.get(self.list_url, {"title": "  cArEeR  "})
        missing = self.client.get(self.list_url, {"title": "unrelated"})

        ordered_ids = [str(recent.pk), str(self.career.pk), str(self.community.pk)]
        self.assertEqual([item["id"] for item in full.data], ordered_ids)
        self.assertEqual([item["id"] for item in blank.data], ordered_ids)
        self.assertEqual([item["id"] for item in matched.data], [str(self.career.pk)])
        self.assertEqual(missing.data, [])

    def test_anonymous_can_read_but_cannot_create_patch_or_delete(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

        for method, url, data in (
            ("post", self.list_url, self.payload),
            ("patch", self.detail_url, {"title": "Forbidden"}),
            ("delete", self.detail_url, None),
        ):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, data, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assert_original_data_unchanged()

    def test_ordinary_user_can_read_but_cannot_manage_experiences(self):
        self.client.force_authenticate(user=self.ordinary)
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

        for method, url, data in (
            ("post", self.list_url, self.payload),
            ("patch", self.detail_url, {"title": "Forbidden"}),
            ("put", self.detail_url, self.payload),
            ("delete", self.detail_url, None),
        ):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, data, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assert_original_data_unchanged()

    def test_editor_can_patch_and_put_complete_payload(self):
        self.client.force_authenticate(user=self.editor)

        patched = self.client.patch(
            self.detail_url, {"title": "Edited career"}, format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.career.refresh_from_db()
        self.assertEqual(self.career.title, "Edited career")
        self.assertEqual(self.career.description, "Built a design system")

        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.career.refresh_from_db()
        self.assertEqual(self.career.title, self.payload["title"])
        self.assertEqual(self.career.description, self.payload["description"])
        self.assertEqual(self.career.category, self.payload["category"])
        self.assertEqual(self.career.thumbnail, self.payload["thumbnail"])
        self.assertEqual(Experience.objects.count(), 2)

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        created = self.client.post(self.list_url, self.payload, format="json")
        deleted = self.client.delete(self.detail_url)

        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_original_data_unchanged()

    def test_superuser_can_create_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        created = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        created_id = created.data["id"]
        detail_url = reverse("api:experience-detail", args=[created_id])
        self.assertEqual(Experience.objects.get(pk=created_id).title, self.payload["title"])

        patched = self.client.patch(
            detail_url, {"title": "Patched chapter"}, format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(Experience.objects.get(pk=created_id).title, "Patched chapter")

        replaced = self.client.put(
            detail_url, {**self.payload, "title": "Replaced chapter"}, format="json",
        )
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.assertEqual(Experience.objects.get(pk=created_id).title, "Replaced chapter")

        deleted = self.client.delete(detail_url)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Experience.objects.filter(pk=created_id).exists())
        self.assertEqual(Experience.objects.count(), 2)

    def test_html_tags_are_stripped_and_sanitized_values_are_saved(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "  <b>Clean chapter</b>  ",
                "description": "  <p>Useful work</p>  ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Clean chapter")
        self.assertEqual(response.data["description"], "Useful work")
        saved = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(saved.title, "Clean chapter")
        self.assertEqual(saved.description, "Useful work")

    def test_text_that_becomes_empty_after_sanitizing_is_rejected(self):
        self.client.force_authenticate(user=self.owner)
        for field, value in (
            ("title", "<b> </b>"),
            ("description", "<p> </p>"),
        ):
            with self.subTest(field=field):
                response = self.client.post(
                    self.list_url,
                    {**self.payload, field: value},
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.assert_original_data_unchanged()

    def test_end_date_before_start_date_is_rejected_on_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "ended_at": "2024-12-31T09:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_at", response.data)
        self.assert_original_data_unchanged()

    def test_patch_checks_submitted_date_against_stored_date(self):
        self.client.force_authenticate(user=self.editor)
        original_start = self.career.started_at
        original_end = self.career.ended_at

        response = self.client.patch(
            self.detail_url,
            {"started_at": "2025-01-01T09:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_at", response.data)
        self.career.refresh_from_db()
        self.assertEqual(self.career.started_at, original_start)
        self.assertEqual(self.career.ended_at, original_end)

    def test_nullable_fields_and_equal_dates_are_accepted(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "thumbnail": None,
                "started_at": None,
                "ended_at": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertIsNone(created.thumbnail)
        self.assertIsNone(created.started_at)
        self.assertIsNone(created.ended_at)

        detail_url = reverse("api:experience-detail", args=[created.pk])
        equal_time = "2025-04-01T09:00:00Z"
        updated = self.client.patch(
            detail_url,
            {"started_at": equal_time, "ended_at": equal_time},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        created.refresh_from_db()
        self.assertEqual(created.started_at, created.ended_at)

        cleared = self.client.patch(
            detail_url,
            {"started_at": None, "ended_at": None, "thumbnail": None},
            format="json",
        )
        self.assertEqual(cleared.status_code, status.HTTP_200_OK)
        created.refresh_from_db()
        self.assertIsNone(created.started_at)
        self.assertIsNone(created.ended_at)
        self.assertIsNone(created.thumbnail)

    def test_id_star_fields_and_relationship_cannot_be_assigned(self):
        self.career.starred_by.add(self.ordinary)
        self.client.force_authenticate(user=self.owner)
        forged_id = uuid.uuid4()

        response = self.client.patch(
            self.detail_url,
            {
                "id": str(forged_id),
                "title": "Safe update",
                "star_count": 999,
                "is_starred": True,
                "starred_by": [self.owner.pk],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.career.pk))
        self.assertEqual(response.data["star_count"], 1)
        self.assertFalse(response.data["is_starred"])
        self.assertNotIn("starred_by", response.data)
        self.career.refresh_from_db()
        self.assertEqual(self.career.title, "Safe update")
        self.assertFalse(Experience.objects.filter(pk=forged_id).exists())
        self.assertEqual(
            list(self.career.starred_by.values_list("pk", flat=True)),
            [self.ordinary.pk],
        )

    def test_unknown_valid_uuids_return_404(self):
        missing_id = uuid.uuid4()
        missing_detail = reverse("api:experience-detail", args=[missing_id])
        missing_star = reverse("api:experience-star", args=[missing_id])

        detail = self.client.get(missing_detail)
        self.client.force_authenticate(user=self.ordinary)
        star = self.client.post(missing_star)

        self.assertEqual(detail.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(star.status_code, status.HTTP_404_NOT_FOUND)
        self.assert_original_data_unchanged()

    def test_anonymous_cannot_star_and_star_requires_post(self):
        anonymous = self.client.post(self.star_url)
        self.assertEqual(anonymous.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.career.starred_by.count(), 0)

        self.client.force_authenticate(user=self.ordinary)
        wrong_method = self.client.get(self.star_url)
        self.assertEqual(wrong_method.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.career.starred_by.count(), 0)

    def test_star_toggles_only_request_user_despite_forged_identity(self):
        self.client.force_authenticate(user=self.ordinary)
        forged_identity = {
            "user_id": self.owner.pk,
            "username": self.owner.username,
            "email": self.owner.email,
            "starred_by": [self.owner.pk, self.editor.pk],
        }

        starred = self.client.post(self.star_url, forged_identity, format="json")
        self.assertEqual(starred.status_code, status.HTTP_200_OK)
        self.assertEqual(starred.data["star_count"], 1)
        self.assertTrue(starred.data["is_starred"])
        self.assertNotIn("starred_by", starred.data)
        self.assertEqual(
            list(self.career.starred_by.values_list("pk", flat=True)),
            [self.ordinary.pk],
        )

        unstarred = self.client.post(self.star_url, forged_identity, format="json")
        self.assertEqual(unstarred.status_code, status.HTTP_200_OK)
        self.assertEqual(unstarred.data["star_count"], 0)
        self.assertFalse(unstarred.data["is_starred"])
        self.assertEqual(self.career.starred_by.count(), 0)

    def test_session_authenticated_write_requires_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        # force_authenticate bypasses session login and cannot prove CSRF protection.
        self.assertTrue(client.login(username=self.owner.username, password="testpass123"))

        response = client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assert_original_data_unchanged()
