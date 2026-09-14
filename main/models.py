import uuid
from django.db import models

# Create your models here.


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
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
        default='full-time'
    )

    thumbnail = models.URLField(
        blank=True,
        null=True
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    ended_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

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
