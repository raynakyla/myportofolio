from django.contrib import messages
from django.core import serializers
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import Group, User


# Create your views here.


PORTFOLIO_OWNER = "Rayna Kayla Rayvanka"

EXPERIENCE_GROUPS = (
    {
        "key": "career",
        "title": "Career",
        "subtitle": "Internships & professional experiences",
        "modifier": "career",
    },
    {
        "key": "organizations",
        "title": "Organizations",
        "subtitle": "Leadership & communities",
        "modifier": "organizations",
    },
    {
        "key": "community",
        "title": "Community",
        "subtitle": "Volunteering, committees & mentoring",
        "modifier": "community",
    },
    {
        "key": "competition",
        "title": "Competition",
        "subtitle": "Challenges, competitions & achievements",
        "modifier": "competitions",
    },
    {
        "key": "personal-project",
        "title": "Personal Project",
        "subtitle": "Things I've built, explored & experimented with",
        "modifier": "projects",
    },
    {
        "key": "certification",
        "title": "Certification",
        "subtitle": "Courses, credentials & continuous learning",
        "modifier": "certifications",
    },
)


def show_main(request):
    context = {
        "name": PORTFOLIO_OWNER,
        "npm": "2506657283",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Computer Science student at Universitas Indonesia "
                                        "who somehow keeps ending up in "
                                        "tech projects, events, and creative spaces "
                                        "— usually all at the same time."

        ),
	"last_login": request.COOKIES.get("last_login"),
    }

    return render(request, "main.html", context)


def show_experience(request):
    experiences_query = Experience.objects.order_by(
        "category", "-started_at", "title"
    ).annotate(
        star_count=Count("starred_by", distinct=True),
    )
    if request.user.is_authenticated:
        stars = Experience.starred_by.through.objects.filter(
            experience_id=OuterRef("pk"), user_id=request.user.pk
        )
        experiences_query = experiences_query.annotate(is_starred=Exists(stars))
    else:
        experiences_query = experiences_query.annotate(
            is_starred=Value(False, output_field=BooleanField())
        )
    experiences = list(experiences_query)

    experiences_by_category = {
        group["key"]: [] for group in EXPERIENCE_GROUPS
    }
    for experience in experiences:
        experiences_by_category.setdefault(experience.category, []).append(
            experience
        )

    experience_groups = [
        {
            **group,
            "items": experiences_by_category[group["key"]],
        }
        for group in EXPERIENCE_GROUPS
    ]

    context = {
        "name": PORTFOLIO_OWNER,
        "experience_list": experiences,
        "experience_groups": experience_groups,
        "can_edit_experience": request.user.is_authenticated and (
            request.user.is_superuser or is_editor(request.user)
        ),
    }

    return render(request, "experience.html", context)


@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST if request.method == "POST" else None)

    if request.method == "POST" and form.is_valid():
        experience = form.save()
        messages.success(
            request,
            f'"{experience.title}" has been added successfully.',
        )
        return redirect("main:show_experience")

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
        "is_update": False,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(
        request.POST if request.method == "POST" else None,
        instance=experience,
    )

    if request.method == "POST" and form.is_valid():
        updated_experience = form.save()
        messages.success(
            request,
            f'"{updated_experience.title}" has been updated successfully.',
        )
        return redirect("main:show_experience")

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
        "experience": experience,
        "is_update": True,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
@require_POST
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    experience_title = experience.title
    experience.delete()
    messages.success(
        request,
        f'"{experience_title}" has been deleted successfully.',
    )
    return redirect("main:show_experience")


def get_experiences_json(request):
    experiences = Experience.objects.order_by(
        "category",
        "-started_at",
        "title",
    )
    experiences_json = serializers.serialize(
        "json",
        experiences,
        fields=(
            "title", "description", "category", "thumbnail", "started_at", "ended_at"
        ),
        use_natural_foreign_keys=True,
    )
    return HttpResponse(experiences_json, content_type="application/json")


@login_required(login_url="/login/")
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)
    return redirect("main:show_experience")


def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    context = {
        "name": PORTFOLIO_OWNER,
        "project_list": projects,
        "title_query": title_query,
    }

    return render(request, "projects.html", context)

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Your new project has been added successfully!",
        )

        return redirect("main:show_projects")

    context = {
        "name": PORTFOLIO_OWNER,
        "form": form,
    }

    return render(request, "projects_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()

    projects = Project.objects.annotate(
        star_count=Count("starred_by", distinct=True),
    )
    if request.user.is_authenticated:
        stars = Project.starred_by.through.objects.filter(
            project_id=OuterRef("pk"), user_id=request.user.pk,
        )
        projects = projects.annotate(is_starred=Exists(stars))
    else:
        projects = projects.annotate(
            is_starred=Value(False, output_field=BooleanField()),
        )

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    project_data = [
        {
            "id": str(project.pk),
            "title": project.title,
            "description": project.description,
            "category_display": project.get_category_display(),
            "role": project.role,
            "skills": project.skills,
            "thumbnail": project.thumbnail,
            "project_url": project.project_url,
            "is_featured": project.is_featured,
            "star_count": project.star_count,
            "is_starred": project.is_starred,
        }
        for project in projects
    ]
    response = JsonResponse(project_data, safe=False)
    response["Cache-Control"] = "private, no-store"
    return response

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    project = get_object_or_404(
        Project,
        pk=project_id,
    )

    if request.method == "POST":
        project_title = project.title
        project.delete()

        messages.success(
            request,
            f'"{project_title}" has been deleted successfully.',
        )

    return redirect("main:show_projects")

# tutorial 4 (biar nyarinya gampang)

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your account has been successfully created!"
            )
            return redirect("main:login")

    context = {
        "form": form
    }

    return render(request, "register.html", context)

# tutorial 4

def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            response = redirect("main:show_main")

            response.set_cookie(
                "last_login",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            return response

    else:
        form = AuthenticationForm(request)

    context = {
        "form": form
    }

    return render(request, "login.html", context)

# tutorial 4
def logout_user(request):
    logout(request)

    response = redirect("main:show_main")
    response.delete_cookie("last_login")

    return response

# tutorial 4
@require_POST
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.user in project.starred_by.all():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)

    return redirect("main:show_projects")

# tugas 4
def is_editor(user):
    return user.groups.filter(name="Editor").exists()
