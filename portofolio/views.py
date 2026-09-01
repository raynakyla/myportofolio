from django.shortcuts import render

def show_main(request):
    context = {
        'npm': '2506657283',
        'name': 'Rayna Kayla Rayvanka',
        'class': 'PBP F',
        'description': 'Mahasiswa Ilmu Komputer',
    }

    return render(request, 'main.html', context)