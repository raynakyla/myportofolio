import json
import uuid
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

# Create your tests here.

from main.models import Experience, Project
from django.contrib.auth.models import User

class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Presales Engineer Intern",
            description=(
                "Supported IT infrastructure presales through product research, "
                "BOQ preparation, requirement analysis, and technical solution support."
            ),
            category="career",
        )

        self.superuser = User.objects.create_superuser(
            username="cheycherry",
            email="convigure@gmail.com",
            password="fortesting"
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
            "career"
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
            "Career"
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


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Sample project",
            description="A prototype for collaborative learning.",
            category="product",
            role="Designer",
            skills="UX Design, Prototyping",
        )

        self.superuser = User.objects.create_superuser(
            username="cheycherry",
            email="convigure@gmail.com",
            password="fortesting"
        )

    def test_projects_url_and_template(self):
        self.assertEqual(reverse("main:show_projects"), "/projects/")
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")
        self.assertEqual(list(response.context["project_list"]), [self.project])

    def test_projects_ajax_shell_keeps_server_permission_controls(self):
        response = self.client.get(reverse("main:show_projects"))
        for element_id in (
            "projects-loading", "projects-error", "projects-empty", "projects-grid",
        ):
            self.assertContains(response, f'id="{element_id}"')
        self.assertContains(response, 'src="/static/js/projects.js"')
        self.assertContains(response, reverse("main:get_projects_json"))
        self.assertNotContains(response, "data-delete-url-template")

        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "data-delete-url-template")

    def test_projects_api_exposes_card_data_without_user_ids(self):
        regular = User.objects.create_user(username="reader", password="secret")
        other = User.objects.create_user(username="another", password="secret")
        self.project.starred_by.add(regular, other)
        url = reverse("main:get_projects_json")

        anonymous_response = self.client.get(url)
        self.assertEqual(anonymous_response.status_code, 200)
        self.assertEqual(anonymous_response["Cache-Control"], "private, no-store")
        anonymous_project = anonymous_response.json()[0]
        self.assertEqual(anonymous_project["star_count"], 2)
        self.assertFalse(anonymous_project["is_starred"])
        self.assertEqual(anonymous_project["category_display"], "Product & UX")
        self.assertEqual(anonymous_project["id"], str(self.project.pk))
        self.assertEqual(
            set(anonymous_project),
            {
                "id", "title", "description", "category_display", "role",
                "skills", "thumbnail", "project_url", "is_featured",
                "star_count", "is_starred",
            },
        )
        self.assertNotIn(regular.username, anonymous_response.content.decode())

        self.client.force_login(regular)
        starred_project = self.client.get(url).json()[0]
        self.assertTrue(starred_project["is_starred"])
        self.assertEqual(starred_project["star_count"], 2)
        self.assertEqual(self.client.get(url, {"title": "missing"}).json(), [])

    def test_create_project_form_is_accessible(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        for field_name in [
            "title",
            "description",
            "category",
            "role",
            "skills",
            "thumbnail",
            "project_url",
            "is_featured",
        ]:
            self.assertContains(response, f'name="{field_name}"')

    def test_create_project_with_valid_form(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Tutorial 3 project",
                "description": "Created through the project form.",
                "category": "web",
                "role": "Developer",
                "skills": "Django, HTML, CSS",
                "thumbnail": "",
                "project_url": "",
            },
        )

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Tutorial 3 project").exists())

    def test_create_project_rejects_invalid_form(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "",
                "description": "Missing a required title.",
                "category": "web",
                "role": "Developer",
                "skills": "Django",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "title", "This field is required.")
        self.assertFalse(Project.objects.filter(description="Missing a required title.").exists())

    def test_project_content_and_optional_fields_absent(self):
        response = self.client.get(reverse("main:show_projects"))
        for value in [self.project.title, self.project.description,
                      self.project.role, self.project.skills, "Product &amp; UX"]:
            self.assertContains(response, value)
        self.assertContains(response, 'class="project-placeholder"')
        self.assertNotContains(response, "View Project")
        self.assertNotContains(response, "Featured")
        self.assertNotContains(response, 'class="project-thumbnail"')

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "No projects have been added yet.")
        self.assertNotContains(response, "View Project")

    def test_project_model(self):
        import uuid

        self.assertEqual(str(self.project), self.project.title)
        self.assertIsInstance(self.project.id, uuid.UUID)
        self.assertEqual(self.project.thumbnail, "")
        self.assertEqual(self.project.project_url, "")
        self.assertFalse(self.project.is_featured)
        self.project.full_clean()

    def test_featured_thumbnail_and_project_link(self):
        self.project.is_featured = True
        self.project.thumbnail = "https://example.com/preview.png"
        self.project.project_url = "https://example.com/project/"
        self.project.save()
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "Featured")
        self.assertContains(response, "View Project")
        self.assertContains(response, f'href="{self.project.project_url}"')
        self.assertContains(response, f'src="{self.project.thumbnail}"')
        self.assertContains(response, f'alt="Preview of {self.project.title}"')
        self.assertNotContains(response, 'class="project-placeholder"')

    def test_all_projects_displayed_in_featured_then_title_order(self):
        featured_z = Project.objects.create(
            title="Z project", category="web", description="Website",
            role="Developer", skills="Django", is_featured=True,
        )
        featured_a = Project.objects.create(
            title="A project", category="creative", description="Illustration",
            role="Artist", skills="Drawing", is_featured=True,
        )
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(list(response.context["project_list"]),
                         [featured_a, featured_z, self.project])
        for project in [featured_a, featured_z, self.project]:
            self.assertContains(response, project.title)
        self.assertContains(response, "Web Development")
        self.assertContains(response, "Creative Work")

    def test_navigation_and_footer_on_all_pages(self):
        routes = ["main:show_main", "main:show_experience", "main:show_projects"]
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
                for target in routes:
                    self.assertContains(response, f'href="{reverse(target)}"')
                self.assertContains(response, "Fakultas Ilmu Komputer, Universitas Indonesia.")


class ExperienceManagementTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Head of Event Division - DDP0 2026",
            description="Led the event division and coordinated its programs.",
            category="community",
            thumbnail="",
            started_at=timezone.now().replace(second=0, microsecond=0),
        )

        self.superuser = User.objects.create_superuser(
            username="experience_admin",
            email="experienceadmin@example.com",
            password="testpass123",
        )

        self.client.force_login(self.superuser)

    def experience_payload(self, **overrides):
        payload = {
            "title": "BEM Fasilkom UI",
            "description": "Contributed to creative student programs.",
            "category": "organizations",
            "thumbnail": "",
            "started_at": self.experience.started_at.strftime("%Y-%m-%dT%H:%M"),
            "ended_at": "",
        }
        payload.update(overrides)
        return payload

    def test_experience_page_and_form_are_accessible(self):
        page_response = self.client.get(reverse("main:show_experience"))
        form_response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(page_response.status_code, 200)
        self.assertTemplateUsed(page_response, "experience.html")
        self.assertEqual(form_response.status_code, 200)
        self.assertTemplateUsed(form_response, "experience_form.html")
        self.assertContains(form_response, "csrfmiddlewaretoken")

        for field_name in [
            "title",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]:
            self.assertContains(form_response, f'name="{field_name}"')

    def test_create_experience_with_valid_form(self):
        response = self.client.post(
            reverse("main:create_experience"),
            self.experience_payload(),
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        created = Experience.objects.get(title="BEM Fasilkom UI")
        self.assertEqual(created.category, "organizations")

    def test_create_experience_rejects_invalid_form_and_keeps_input(self):
        response = self.client.post(
            reverse("main:create_experience"),
            self.experience_payload(
                title="",
                description="Keep this description in the form.",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "title",
            "This field is required.",
        )
        self.assertContains(response, "Keep this description in the form.")
        self.assertFalse(
            Experience.objects.filter(
                description="Keep this description in the form."
            ).exists()
        )

    def test_update_form_is_prefilled(self):
        response = self.client.get(
            reverse(
                "main:update_experience",
                args=[self.experience.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].instance, self.experience)
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)

    def test_update_changes_same_object_without_adding_another(self):
        original_id = self.experience.id
        original_count = Experience.objects.count()
        response = self.client.post(
            reverse(
                "main:update_experience",
                args=[self.experience.id],
            ),
            self.experience_payload(
                title="Updated Event Lead",
                category="competition",
            ),
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertEqual(Experience.objects.count(), original_count)
        updated = Experience.objects.get(pk=original_id)
        self.assertEqual(updated.title, "Updated Event Lead")
        self.assertEqual(updated.category, "competition")

    def test_invalid_update_does_not_change_saved_data(self):
        original_title = self.experience.title
        response = self.client.post(
            reverse(
                "main:update_experience",
                args=[self.experience.id],
            ),
            self.experience_payload(title=""),
        )

        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, original_title)
        self.assertEqual(Experience.objects.count(), 1)

    def test_end_date_cannot_precede_start_date(self):
        invalid_end = self.experience.started_at - timedelta(days=1)
        response = self.client.post(
            reverse(
                "main:update_experience",
                args=[self.experience.id],
            ),
            self.experience_payload(
                title=self.experience.title,
                ended_at=invalid_end.strftime("%Y-%m-%dT%H:%M"),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "ended_at",
            "End date and time cannot be earlier than the start date and time.",
        )
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)

    def test_delete_requires_post_and_post_deletes(self):
        delete_url = reverse(
            "main:delete_experience",
            args=[self.experience.id],
        )

        get_response = self.client.get(delete_url)
        self.assertEqual(get_response.status_code, 405)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

        post_response = self.client.post(delete_url)
        self.assertRedirects(post_response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_missing_experience_ids_return_404(self):
        missing_id = uuid.uuid4()

        update_response = self.client.get(
            reverse("main:update_experience", args=[missing_id])
        )
        delete_response = self.client.post(
            reverse("main:delete_experience", args=[missing_id])
        )

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)

    def test_experience_json_endpoint_is_valid(self):
        response = self.client.get(reverse("main:get_experiences_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = json.loads(response.content)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["pk"], str(self.experience.id))
        self.assertEqual(
            payload[0]["fields"]["title"],
            self.experience.title,
        )

    def test_experience_page_displays_saved_data_and_json_still_works(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Head of Event Division - DDP0 2026")
        self.assertEqual(
            response.context["experience_list"][0].title,
            "Head of Event Division - DDP0 2026",
        )
        json_response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(
            json_response.json()[0]["fields"]["title"], self.experience.title
        )

    def test_empty_experience_page_and_category_structure(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")
        for category_title in [
            "Career",
            "Organizations",
            "Community",
            "Competition",
            "Personal Project",
            "Certification",
        ]:
            self.assertContains(response, category_title)

    def test_profile_and_projects_still_work(self):
        for route_name, template_name in [
            ("main:show_main", "main.html"),
            ("main:show_projects", "projects.html"),
        ]:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template_name)

    ''' def test_anonymous_cannot_create_experience(self):
        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 302)

    def test_regular_user_cannot_create_experience(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 403)

    def test_editor_cannot_create_experience(self):
        self.client.force_login(self.editor_user)

        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_create_experience(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 200) '''
