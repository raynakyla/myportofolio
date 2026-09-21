import uuid
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ("career", "Career"),
        ("organizations", "Organizations"),
        ("community", "Community"),
        ("competition", "Competition"),
        ("personal-project", "Personal Project"),
        ("certification", "Certification"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default="career",
    )

    thumbnail = models.URLField(
        blank=True,
        null=True
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    ended_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if (
            self.started_at
            and self.ended_at
            and self.ended_at < self.started_at
        ):
            raise ValidationError(
                {
                    "ended_at": (
                        "End date and time cannot be earlier than "
                        "the start date and time."
                    )
                }
            )

    @property
    def is_ongoing(self):
        return self.ended_at is None


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('product', 'Product & UX'),
        ('creative', 'Creative Work'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    role = models.CharField(max_length=255)
    skills = models.CharField(max_length=255)
    thumbnail = models.URLField(blank=True, default='')
    project_url = models.URLField(blank=True, default='')
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_featured', 'title']

    def __str__(self):
        return self.title
