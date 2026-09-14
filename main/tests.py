from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

# Create your tests here.

from main.models import Experience, Project


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


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Sample project",
            description="A prototype for collaborative learning.",
            category="product",
            role="Designer",
            skills="UX Design, Prototyping",
        )

    def test_projects_url_and_template(self):
        self.assertEqual(reverse("main:show_projects"), "/projects/")
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")
        self.assertEqual(list(response.context["project_list"]), [self.project])

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
