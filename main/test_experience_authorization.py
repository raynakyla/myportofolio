"""Authorization and star behavior for the Experience feature."""

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Experience, Project


class ExperienceAuthorizationTests(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="A chapter",
            description="A portfolio experience",
            category="career",
        )
        self.regular = User.objects.create_user("regular", password="testpass123")
        self.editor = User.objects.create_user("editor", password="testpass123")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.owner = User.objects.create_superuser(
            "owner", "owner@example.com", "testpass123"
        )
        self.page_url = reverse("main:show_experience")
        self.create_url = reverse("main:create_experience")
        self.update_url = reverse("main:update_experience", args=[self.experience.pk])
        self.delete_url = reverse("main:delete_experience", args=[self.experience.pk])
        self.star_url = reverse("main:toggle_experience_star", args=[self.experience.pk])
        self.payload = {
            "title": "Another chapter",
            "description": "A new experience",
            "category": "community",
            "thumbnail": "",
            "started_at": "",
            "ended_at": "",
        }

    def test_anonymous_can_read_but_mutations_redirect_to_login(self):
        self.assertEqual(self.client.get(self.page_url).status_code, 200)
        for url, method in (
            (self.create_url, "get"),
            (self.update_url, "get"),
            (self.delete_url, "post"),
            (self.star_url, "post"),
        ):
            with self.subTest(url=url):
                response = getattr(self.client, method)(url)
                self.assertRedirects(
                    response, f"/login/?next={url}", fetch_redirect_response=False
                )
        self.assertEqual(self.client.get(self.delete_url).status_code, 302)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_regular_user_can_star_but_cannot_manage_experiences(self):
        self.client.force_login(self.regular)
        self.assertEqual(self.client.get(self.page_url).status_code, 200)
        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        self.assertEqual(self.client.post(self.create_url, self.payload).status_code, 403)
        self.assertEqual(self.client.get(self.update_url).status_code, 403)
        self.assertEqual(self.client.post(self.update_url, self.payload).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertRedirects(self.client.post(self.star_url), self.page_url)
        self.assertEqual(self.experience.starred_by.count(), 1)
        self.assertTrue(self.experience.starred_by.filter(pk=self.regular.pk).exists())

    def test_editor_can_update_and_star_but_cannot_create_or_delete(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(self.page_url).status_code, 200)
        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        self.assertEqual(self.client.post(self.create_url, self.payload).status_code, 403)
        self.assertEqual(self.client.get(self.update_url).status_code, 200)
        self.assertRedirects(self.client.post(self.update_url, self.payload), self.page_url)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, self.payload["title"])
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertRedirects(self.client.post(self.star_url), self.page_url)
        self.assertEqual(self.experience.starred_by.count(), 1)

    def test_superuser_can_create_update_star_and_delete(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.page_url).status_code, 200)
        self.assertEqual(self.client.get(self.create_url).status_code, 200)
        self.assertRedirects(self.client.post(self.create_url, self.payload), self.page_url)
        self.assertTrue(Experience.objects.filter(title=self.payload["title"]).exists())
        self.assertEqual(self.client.get(self.update_url).status_code, 200)
        self.assertRedirects(self.client.post(self.update_url, self.payload), self.page_url)
        self.assertRedirects(self.client.post(self.star_url), self.page_url)
        self.assertEqual(self.experience.starred_by.count(), 1)
        self.assertRedirects(self.client.post(self.delete_url), self.page_url)
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_star_toggles_only_current_user_and_count_is_visible(self):
        self.client.force_login(self.regular)
        self.client.post(self.star_url)
        self.client.force_login(self.editor)
        self.client.post(self.star_url)
        self.assertEqual(self.experience.starred_by.count(), 2)
        response = self.client.get(self.page_url)
        item = response.context["experience_list"][0]
        self.assertEqual(item.star_count, 2)
        self.assertTrue(item.is_starred)
        self.assertContains(response, 'aria-label="Unstar A chapter"')

        self.client.post(self.star_url)
        self.assertEqual(self.experience.starred_by.count(), 1)
        self.assertTrue(self.experience.starred_by.filter(pk=self.regular.pk).exists())
        self.assertFalse(self.experience.starred_by.filter(pk=self.editor.pk).exists())
        self.client.post(self.star_url)
        self.assertEqual(self.experience.starred_by.count(), 2)
        self.assertEqual(
            self.experience.starred_by.through.objects.filter(
                experience_id=self.experience.pk, user_id=self.editor.pk
            ).count(),
            1,
        )

    def test_star_requires_post_and_csrf(self):
        self.client.force_login(self.regular)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.regular)
        self.assertEqual(csrf_client.post(self.star_url).status_code, 403)
        csrf_client.get(self.page_url)
        token = csrf_client.cookies["csrftoken"].value
        self.assertRedirects(
            csrf_client.post(self.star_url, {"csrfmiddlewaretoken": token}),
            self.page_url,
        )
        self.assertEqual(self.experience.starred_by.count(), 1)

    def test_role_specific_controls_and_public_count(self):
        self.experience.starred_by.add(self.owner)
        for user, can_create, can_edit, can_delete in (
            (None, False, False, False),
            (self.regular, False, False, False),
            (self.editor, False, True, False),
            (self.owner, True, True, True),
        ):
            with self.subTest(role=user.username if user else "anonymous"):
                if user:
                    self.client.force_login(user)
                else:
                    self.client.logout()
                response = self.client.get(self.page_url)
                self.assertContains(response, self.experience.title)
                self.assertContains(response, f'action="{self.star_url}"')
                self.assertEqual(
                    f'href="{self.create_url}"' in response.content.decode(),
                    can_create,
                )
                self.assertEqual(
                    f'href="{self.update_url}"' in response.content.decode(),
                    can_edit,
                )
                self.assertEqual(
                    f'popovertarget="delete-experience-{self.experience.pk}"'
                    in response.content.decode(),
                    can_delete,
                )
                self.assertEqual(response.context["experience_list"][0].star_count, 1)
                if user is None:
                    self.assertContains(response, "Sign in to star A chapter")

    def test_public_json_excludes_starring_user_ids(self):
        self.experience.starred_by.add(self.regular)
        response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["fields"]["title"], self.experience.title)
        self.assertNotIn("starred_by", response.json()[0]["fields"])

    def test_existing_project_star_still_works(self):
        project = Project.objects.create(
            title="Project", description="Details", category="web",
            role="Developer", skills="Django",
        )
        self.client.force_login(self.regular)
        url = reverse("main:toggle_star", args=[project.pk])
        self.assertRedirects(self.client.post(url), reverse("main:show_projects"))
        self.assertEqual(project.starred_by.count(), 1)
