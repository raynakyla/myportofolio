import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project


class ProjectAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            title="Django Portfolio",
            description="A personal website",
            category="web",
            role="Developer",
            skills="Django, Python",
        )
        cls.ordinary = User.objects.create_user(username="reader")
        cls.staff = User.objects.create_user(username="staff", is_staff=True)
        cls.editor = User.objects.create_user(username="editor")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.owner = User.objects.create_user(
            username="owner", is_staff=True, is_superuser=True,
        )

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.pk])
        self.star_url = reverse("api:project-star", args=[self.project.pk])
        self.payload = {
            "title": "New Portfolio Project",
            "description": "A new project",
            "category": "product",
            "role": "Designer",
            "skills": "Research, Figma",
            "thumbnail": "https://example.com/preview.png",
            "project_url": "https://example.com/project/",
            "is_featured": True,
        }

    def test_public_can_retrieve_flat_project_list_and_detail(self):
        listing = self.client.get(self.list_url)
        detail = self.client.get(self.detail_url)

        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 1)
        for item in (listing.data[0], detail.data):
            self.assertEqual(item["id"], str(self.project.pk))
            self.assertEqual(item["category"], "web")
            self.assertIn("skills", item)
            self.assertFalse(item["is_starred"])
            self.assertNotIn("pk", item)
            self.assertNotIn("fields", item)
            self.assertNotIn("starred_by", item)

    def test_title_search_is_case_insensitive_and_can_be_empty(self):
        Project.objects.create(
            title="Illustration", description="Artwork", category="creative",
            role="Artist", skills="Drawing",
        )

        matched = self.client.get(self.list_url, {"title": "dJaNgO"})
        missing = self.client.get(self.list_url, {"title": "absent"})

        self.assertEqual(matched.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in matched.data], [str(self.project.pk)])
        self.assertEqual(missing.status_code, status.HTTP_200_OK)
        self.assertEqual(missing.data, [])

    def test_missing_project_detail_returns_404(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_and_ordinary_users_cannot_manage_projects(self):
        for user in (None, self.ordinary):
            if user is None:
                self.client.logout()
            else:
                self.client.force_login(user)
            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("patch", self.detail_url, {"title": "Changed"}),
                ("delete", self.detail_url, None),
            ):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(url, payload, format="json")
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                    self.assertEqual(Project.objects.count(), 1)
                    self.project.refresh_from_db()
                    self.assertEqual(self.project.title, "Django Portfolio")
                    self.assertEqual(self.project.description, "A personal website")

    def test_superuser_can_create_project(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Project.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, self.payload["title"])
        self.assertEqual(created.skills, self.payload["skills"])
        self.assertTrue(created.is_featured)

    def test_invalid_title_and_url_cannot_create_projects(self):
        self.client.force_login(self.owner)
        for changes, field in (
            ({"title": "   "}, "title"),
            ({"title": "<b> </b>"}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ):
            with self.subTest(changes=changes):
                response = self.client.post(
                    self.list_url, {**self.payload, **changes}, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.assertEqual(Project.objects.count(), 1)

    def test_superuser_can_patch_put_and_delete_project(self):
        self.client.force_login(self.owner)

        patched = self.client.patch(
            self.detail_url, {"title": "Updated title"}, format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated title")
        self.assertEqual(self.project.description, "A personal website")
        self.assertEqual(self.project.skills, "Django, Python")

        incomplete = self.client.put(
            self.detail_url, {"title": "Incomplete"}, format="json",
        )
        self.assertEqual(incomplete.status_code, status.HTTP_400_BAD_REQUEST)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated title")

        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, self.payload["title"])
        self.assertEqual(self.project.category, self.payload["category"])
        self.assertEqual(self.project.role, self.payload["role"])
        self.assertEqual(self.project.skills, self.payload["skills"])

        deleted = self.client.delete(self.detail_url)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_star_requires_login_and_toggles_for_authenticated_user(self):
        anonymous = self.client.post(self.star_url)
        self.assertEqual(anonymous.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.project.starred_by.count(), 0)

        self.client.force_login(self.ordinary)
        starred = self.client.post(self.star_url)
        self.assertEqual(starred.status_code, status.HTTP_200_OK)
        self.assertTrue(starred.data["is_starred"])
        self.assertEqual(starred.data["star_count"], 1)
        self.assertTrue(self.project.starred_by.filter(pk=self.ordinary.pk).exists())

        unstarred = self.client.post(self.star_url)
        self.assertEqual(unstarred.status_code, status.HTTP_200_OK)
        self.assertFalse(unstarred.data["is_starred"])
        self.assertEqual(unstarred.data["star_count"], 0)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_computed_star_fields_and_relationship_are_read_only(self):
        self.client.force_login(self.owner)
        forged_id = uuid.uuid4()
        forged = {
            **self.payload,
            "id": str(forged_id),
            "star_count": 999,
            "is_starred": True,
            "starred_by_names": "reader",
            "starred_by": [self.ordinary.pk],
        }

        response = self.client.post(self.list_url, forged, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], str(forged_id))
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")
        self.assertNotIn("starred_by", response.data)
        self.assertEqual(Project.objects.get(pk=response.data["id"]).starred_by.count(), 0)

    def test_staff_and_editor_cannot_manage_projects(self):
        for user in (self.staff, self.editor):
            self.client.force_login(user)
            for method, url, payload in (
                ("post", self.list_url, self.payload),
                ("patch", self.detail_url, {"title": "Changed"}),
                ("delete", self.detail_url, None),
            ):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(url, payload, format="json")
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                    self.assertEqual(Project.objects.count(), 1)
                    self.project.refresh_from_db()
                    self.assertEqual(self.project.title, "Django Portfolio")

    def test_unsupported_list_delete_returns_405(self):
        self.client.force_login(self.owner)
        response = self.client.delete(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.owner)

        response = client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_browsable_api_csrf_token_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.owner)
        browsable = client.get(self.list_url, HTTP_ACCEPT="text/html")

        self.assertEqual(browsable.status_code, status.HTTP_200_OK)
        self.assertContains(browsable, 'name="csrfmiddlewaretoken"')
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())
