from django.shortcuts import render, redirect
from .forms import EmployeeForm, WorkCategoryForm, WorkHoursForm, CountForm, ProtocolForm
from .models import Employee, WorkCategory, WorkHours, Count, Protocol

def index(request):
    # Initialize all forms
    emp_form = EmployeeForm()
    work_form = WorkCategoryForm()
    hours_form = WorkHoursForm()
    protocol_form = ProtocolForm()
    
    categories = ['Alu', 'Holz', 'Karton', 'Magnetshrott', 'Kanister']
    
    # Create a list of 5 CountForm instances with the fixed category for each
    count_forms = [CountForm(prefix=str(i), initial={'category': category}) for i, category in enumerate(categories)]
    
    if request.method == "POST":
        # Bind the forms to the POST data
        emp_form = EmployeeForm(request.POST)
        work_form = WorkCategoryForm(request.POST)
        hours_form = WorkHoursForm(request.POST)
        protocol_form = ProtocolForm(request.POST)

        # Bind the count forms with the POST data (using prefixes to distinguish each)
        count_forms = [CountForm(request.POST, prefix=str(i), initial={'category': category}) for i, category in enumerate(categories)]

        # Process the forms
        if emp_form.is_valid():
            emp_form.save()
        if work_form.is_valid():
            work_form.save()
        if hours_form.is_valid():
            hours_form.save()

        # Save each count form if valid
        for count_form in count_forms:
            if count_form.is_valid():
                count_form.save()

        if protocol_form.is_valid():
            protocol_form.save()

        return redirect('index')  # Redirect to refresh the page

    # Retrieve any existing records to display in the template
    employees = Employee.objects.all()
    work_categories = WorkCategory.objects.all()
    work_hours = WorkHours.objects.all()
    counts = Count.objects.all()
    protocol = Protocol.objects.first()  # Assuming one protocol record

    # Pass the forms to the template
    return render(request, 'data_entry/index.html', {
        'emp_form': emp_form,
        'work_form': work_form,
        'hours_form': hours_form,
        'count_forms': count_forms,  # Pass the list of count forms
        'protocol_form': protocol_form,
        'employees': employees,
        'work_categories': work_categories,
        'work_hours': work_hours,
        'counts': counts,
        'protocol': protocol,
    })
