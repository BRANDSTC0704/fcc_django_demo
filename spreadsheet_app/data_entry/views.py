from django.shortcuts import render, redirect
from .forms import EmployeeForm, WorkCategoryForm, WorkHoursForm, ContainerCountForm, ProtocolForm
from .models import Employee, WorkCategory, WorkHours, ContainerCount, Protocollist
from datetime import datetime
from contextlib import contextmanager
import locale

def index(request):
    # Initialize all forms
    emp_form = EmployeeForm()
    work_form = WorkCategoryForm()
    hours_form = WorkHoursForm()
    container_form = ContainerCountForm()
    protocol_form = ProtocolForm()
        
    if request.method == "POST":
        # Bind the forms to the POST data
        emp_form = EmployeeForm(request.POST)
        work_form = WorkCategoryForm(request.POST)
        hours_form = WorkHoursForm(request.POST)
        protocol_form = ProtocolForm(request.POST)
        container_form = ContainerCountForm(request.POST)

        # Bind the count forms with the POST data (using prefixes to distinguish each)
        #count_forms = [CountForm(request.POST, prefix=str(i), initial={'category': category}) for i, category in enumerate(categories)]

        # Process the forms
        if emp_form.is_valid():
            emp_form.save()
        if work_form.is_valid():
            work_form.save()
        if hours_form.is_valid():
            hours_form.save()
        if container_form.is_valid():
           container_form.save()
        if protocol_form.is_valid():
            protocol_form.save()

        return redirect('index')  # Redirect to refresh the page

    # Retrieve any existing records to display in the template
    employees = Employee.objects.all()
    work_categories = WorkCategory.objects.all()
    work_hours = WorkHours.objects.all()
    cont_counts = ContainerCount.objects.all()
    protocollist = Protocollist.objects.first()  # Assuming one protocol record

    # heutiges Datum deutsch 
    @contextmanager
    def german_locale():
        old_locale = locale.getlocale()  # Save the current locale
        try:
            locale.setlocale(locale.LC_TIME, "de_DE")  # Set German locale
            yield  # Allow code execution inside the context
        finally:
            locale.setlocale(locale.LC_TIME, old_locale)  # Restore previous locale

    # Usage
    with german_locale():
        today = datetime.today().strftime("%A, %d. %B %Y")  # German format
    
    # Pass the forms to the template
    return render(request, 'data_entry/index.html', {
        'emp_form': emp_form,
        'work_form': work_form,
        'hours_form': hours_form,
        'container_form': container_form,  # Pass the list of count forms
        'protocol_form': protocol_form,
        'employees': employees,
        'work_categories': work_categories,
        'work_hours': work_hours,
        'cont_counts': cont_counts,
        'protocollist': protocollist,
        'heute': today
    })
