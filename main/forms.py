from django.forms import (
    CheckboxInput,
    ModelForm,
    Select,
    Textarea,
    TextInput,
    URLInput,
)

from main.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project

        fields = [
            "title",
            "description",
            "category",
            "role",
            "skills",
            "thumbnail",
            "project_url",
            "is_featured",
        ]

        labels = {
            "title": "Project Title",
            "description": "Description",
            "category": "Category",
            "role": "My Role",
            "skills": "Skills",
            "thumbnail": "Thumbnail URL",
            "project_url": "Project URL",
            "is_featured": "Featured Project",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Tell us about your project",
                    "rows": 4,
                }
            ),
            "category": Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "role": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "UI/UX Designer, Frontend Developer, etc.",
                    "maxlength": 255,
                }
            ),
            "skills": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Django, Python, HTML, CSS",
                    "maxlength": 255,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/project-image.jpg",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/username/project",
                }
            ),
            "is_featured": CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                }
            ),
        }