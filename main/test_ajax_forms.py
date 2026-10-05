"""AJAX form responses, permissions, and normal form fallbacks."""

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Experience, Project


class ProjectAjaxFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            "project_owner", "project@example.com", "secret"
        )
        self.regular = User.objects.create_user("project_reader", password="secret")
        self.url = reverse("main:create_project")
        self.payload = {
            "title": "New portfolio project",
            "description": "A project created from the modal.",
            "category": "web",
            "role": "Developer",
            "skills": "Django",
            "thumbnail": "",
            "project_url": "",
        }

    def test_superuser_ajax_create_and_normal_post_fallback(self):
        self.client.force_login(self.owner)
        page = self.client.get(reverse("main:show_projects"))
        self.assertContains(page, 'id="project-create-modal"')
        self.assertContains(page, 'id="project-create-form"')
        for name in self.payload:
            self.assertContains(page, f'name="{name}"')

        response = self.client.post(
            self.url, self.payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "success": True,
            "message": "Your new project has been added successfully!",
        })
        self.assertTrue(Project.objects.filter(title=self.payload["title"]).exists())
        titles = [item["fields"]["title"] for item in self.client.get(
            reverse("main:get_projects_json")
        ).json()]
        self.assertIn(self.payload["title"], titles)

        normal = self.client.post(self.url, {**self.payload, "title": "Normal project"})
        self.assertRedirects(normal, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Normal project").exists())

    def test_ajax_validation_and_permission(self):
        self.client.force_login(self.owner)
        invalid = self.client.post(
            self.url,
            {**self.payload, "title": "", "thumbnail": "not-a-url"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertFalse(invalid.json()["success"])
        self.assertIn("title", invalid.json()["errors"])
        self.assertIn("thumbnail", invalid.json()["errors"])
        self.assertEqual(Project.objects.count(), 0)

        self.client.force_login(self.regular)
        self.assertNotContains(
            self.client.get(reverse("main:show_projects")),
            'id="project-create-modal"',
        )
        denied = self.client.post(
            self.url, self.payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(Project.objects.count(), 0)

    def test_ajax_create_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        client.get(reverse("main:show_projects"))
        self.assertEqual(client.post(
            self.url, self.payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        ).status_code, 403)
        response = client.post(
            self.url,
            self.payload,
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 1)


class ExperienceAjaxFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            "experience_owner", "experience@example.com", "secret"
        )
        self.editor = User.objects.create_user("experience_editor", password="secret")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.regular = User.objects.create_user("experience_reader", password="secret")
        self.experience = Experience.objects.create(
            title="Existing chapter",
            description="Original description",
            category="career",
        )
        self.create_url = reverse("main:create_experience")
        self.update_url = reverse(
            "main:update_experience", args=[self.experience.pk]
        )
        self.payload = {
            "title": "New chapter",
            "description": "A chapter created from the modal.",
            "category": "community",
            "thumbnail": "",
            "started_at": "2024-01-01T09:00",
            "ended_at": "",
        }

    def test_create_ajax_success_validation_and_permission(self):
        self.client.force_login(self.owner)
        page = self.client.get(reverse("main:show_experience"))
        self.assertContains(page, 'id="experience-create-modal"')
        self.assertContains(page, 'id="experience-edit-modal"')
        for name in self.payload:
            self.assertContains(page, f'id="id_experience_create_{name}"')
            self.assertContains(page, f'id="id_experience_edit_{name}"')

        created = self.client.post(
            self.create_url, self.payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json(), {
            "success": True,
            "message": '"New chapter" has been added successfully.',
        })
        self.assertTrue(Experience.objects.filter(title="New chapter").exists())

        invalid = self.client.post(
            self.create_url,
            {**self.payload, "title": "", "thumbnail": "not-a-url"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("title", invalid.json()["errors"])
        self.assertIn("thumbnail", invalid.json()["errors"])
        self.assertEqual(Experience.objects.count(), 2)

        for user in (self.editor, self.regular):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertNotContains(
                    self.client.get(reverse("main:show_experience")),
                    'id="experience-create-modal"',
                )
                self.assertEqual(self.client.post(
                    self.create_url, self.payload,
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest",
                ).status_code, 403)

    def test_update_ajax_for_owner_and_editor_with_normal_fallback(self):
        for user, title in ((self.owner, "Owner edit"), (self.editor, "Editor edit")):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                page = self.client.get(reverse("main:show_experience"))
                self.assertContains(page, 'id="experience-edit-modal"')
                response = self.client.post(
                    self.update_url,
                    {**self.payload, "title": title},
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest",
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["message"],
                                 f'"{title}" has been updated successfully.')
                self.experience.refresh_from_db()
                self.assertEqual(self.experience.title, title)
                self.assertEqual(Experience.objects.count(), 1)

        normal = self.client.post(
            self.update_url, {**self.payload, "title": "Normal edit"}
        )
        self.assertRedirects(normal, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Normal edit")

    def test_update_ajax_validation_and_regular_user_restriction(self):
        self.client.force_login(self.owner)
        invalid = self.client.post(
            self.update_url,
            {**self.payload, "ended_at": "2023-01-01T09:00"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("ended_at", invalid.json()["errors"])
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Existing chapter")

        self.client.force_login(self.regular)
        self.assertNotContains(
            self.client.get(reverse("main:show_experience")),
            'id="experience-edit-modal"',
        )
        denied = self.client.post(
            self.update_url, self.payload,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(denied.status_code, 403)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Existing chapter")

    def test_json_has_all_edit_fields_without_user_relations(self):
        fields = self.client.get(reverse("main:get_experiences_json")).json()[0]["fields"]
        for name in self.payload:
            self.assertIn(name, fields)
        self.assertNotIn("starred_by", fields)

    def test_ajax_create_and_update_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        client.get(reverse("main:show_experience"))
        token = client.cookies["csrftoken"].value
        for url in (self.create_url, self.update_url):
            with self.subTest(url=url):
                self.assertEqual(client.post(
                    url, self.payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
                ).status_code, 403)
                response = client.post(
                    url,
                    self.payload,
                    HTTP_X_CSRFTOKEN=token,
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest",
                )
                self.assertEqual(response.status_code, 200)
