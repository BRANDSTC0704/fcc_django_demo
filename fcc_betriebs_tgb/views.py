from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect

def start_page(request):
    return render(request, "start_page.html")

def logout_view(request):
    logout(request)
    return redirect('/')