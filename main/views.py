from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ProjectForm
from main.models import Experience, Project

# Create your views here.

from main.models import Experience, Project


def show_main(request):
    context = {
        "name": "Rayna Kayla Rayvanka",
        "npm": "2506657283",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Computer Science student at Universitas Indonesia "
                                        "who somehow keeps ending up in "
                                        "tech projects, events, and creative spaces "
                                        "— usually all at the same time."

        ),
    }

    return render(request, "main.html", context)


def show_experience(request):
    context = {
        "name": "Rayna Kayla Rayvanka",
        "experience_list": Experience.objects.all(),
    }

    return render(request, "experience.html", context)


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
        "name": "Rayna Kayla Rayvanka",
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
        "name": "Rayna Kayla Rayvanka",
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