from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from datetime import datetime

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
    json_response = get_experiences_json(request)
    deserialized_experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experiences = [item.object for item in deserialized_experiences]

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
    }

    return render(request, "experience.html", context)


def create_experience(request):
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


def update_experience(request, experience_id):
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


@require_POST
def delete_experience(request, experience_id):
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
    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")


def show_projects(request):
    json_response = get_projects_json(request)

    serialized_projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    projects = [
        serialized_project.object
        for serialized_project in serialized_projects
    ]

    title_query = request.GET.get("title", "").strip()

    context = {
        "name": PORTFOLIO_OWNER,
        "project_list": projects,
        "title_query": title_query,
    }

    return render(request, "projects.html", context)


def create_project(request):
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

    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)

    return HttpResponse(
        projects_json,
        content_type="application/json",
    )

def delete_project(request, project_id):
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
def logout_user(request):
    logout(request)

    response = redirect("main:show_main")
    response.delete_cookie("last_login")

    return response