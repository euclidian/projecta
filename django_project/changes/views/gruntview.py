from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect


def grunttest(request):
    return render(request,"grunttest.html")