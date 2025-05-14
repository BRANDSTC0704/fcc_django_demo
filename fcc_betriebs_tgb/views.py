from django.shortcuts import render
from django.contrib.auth import logout
from django.urls import reverse
from django.http import HttpResponseRedirect


def start_page(request):
    return render(request, "start_page.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(("/"))
