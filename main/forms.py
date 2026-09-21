from django.forms import (
    CheckboxInput,
    DateTimeInput,
    ModelForm,
    Select,
    Textarea,
    TextInput,
    URLInput,
)

from main.models import Experience, Project


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]
        labels = {
            "title": "Experience Title",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Thumbnail URL",
            "started_at": "Start Date and Time",
            "ended_at": "End Date and Time",
        }
        help_texts = {
            "started_at": "Optional. Enter the actual start time in UTC, or leave blank if unknown.",
            "ended_at": "Enter the end time in UTC. Leave blank if this experience is still ongoing.",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Head of Event Division",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe what you did and learned.",
                    "rows": 5,
                }
            ),
            "category": Select(attrs={"class": "form-control"}),
            "thumbnail": URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/experience.jpg",
                }
            ),
            "started_at": DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
            ),
            "ended_at": DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"class": "form-control", "type": "datetime-local"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("started_at", "ended_at"):
            self.fields[field_name].input_formats = ["%Y-%m-%dT%H:%M"]


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
