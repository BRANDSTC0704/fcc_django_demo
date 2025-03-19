from django.shortcuts import render

def weekly_dashboard(request):
    return render(request, "dashboards/weekly.html")

def monthly_dashboard(request):
    return render(request, "dashboards/monthly.html")
