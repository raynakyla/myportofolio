from django.shortcuts import render

# Create your views here.

from main.models import Experience


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