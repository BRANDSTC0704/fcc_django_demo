from django.shortcuts import render

# Create your views here.

def grouped_dashboard(request):
    return render(request, "dashboards/grouped_dashboard.html")

