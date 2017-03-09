# Create your views here.
from django.shortcuts import render


def todo(request):
    return render(request, "todo.html")
