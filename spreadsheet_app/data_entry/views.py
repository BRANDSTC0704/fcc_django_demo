from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import EmployeeForm, WorkCategoryForm, WorkHoursForm, ContainerCountForm, ProtocollistForm
from .models import Employee, WorkCategory, WorkHours, ContainerCount, Protocollist
from datetime import datetime
from contextlib import contextmanager
import locale
from django.contrib import messages
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django_plotly_dash.models import StatelessApp
import data_entry.dash_apps  # This ensures the app gets registered

def entrance_page(request): 
    return render(request, 'data_entry/entrance.html')

def form_page(request):

    initial_data = [ 
        {"first_name": "Hamdi", "surname": "Kanak", "attribut": ""},
        {"first_name": "Kurt", "surname": "Kadir", "attribut": ""},
        {"first_name": "Murat", "surname": "Rashidbekov", "attribut": ""},
        {"first_name": "Ali Riza", "surname": "Yaldizli", "attribut": ""},
        {"first_name": "Maher", "surname": "Jendoubi", "attribut": ""},
        {"first_name": "Marko", "surname": "Pranjkovic", "attribut": "Leasing"},
        {"first_name": "Mario", "surname": "Erceg", "attribut": "Leasing"},
        {"first_name": "Engin", "surname": "Enez", "attribut": "Aufgeber"},
        
        ]

    EmployeeFormset = modelformset_factory(Employee, form=EmployeeForm, extra=len(initial_data), can_delete=True)

    if request.method == "POST":
        emp_formset = EmployeeFormset(request.POST)  # Fix: Use only one instance
        work_form = WorkCategoryForm(request.POST)
        hours_form = WorkHoursForm(request.POST)
        container_form = ContainerCountForm(request.POST)
        protocol_form = ProtocollistForm(request.POST)

        if not emp_formset.is_valid(): 
            print('Employee is wrong!')
            print(emp_formset.errors)
            messages.error(request, "❌ In der Mitarbeiter-Maske gibt es falsche oder fehlende Daten!")
        if not work_form.is_valid(): 
            print('Work Form is wrong!')
            messages.error(request, "❌ In der Modul 3 Maske gibt es falsche oder fehlende Daten!")
        if not hours_form.is_valid(): 
            print('Hours is wrong!')
            messages.error(request, "❌ In der Zählerstands-Maske gibt es falsche oder fehlende Daten!")
        if not container_form.is_valid(): 
            print('Container is wrong!')
            messages.error(request, "❌ In der Container-Maske gibt es falsche oder fehlende Daten!")
        if not protocol_form.is_valid(): 
            print('Prot. is wrong!')
            messages.error(request, "❌ In der Protokollisten-Maske gibt es falsche oder fehlende Daten!")

        if  emp_formset.is_valid() and work_form.is_valid() and\
            hours_form.is_valid() and container_form.is_valid() and\
            protocol_form.is_valid():
           
            emp_formset.save()
            work_form.save()
            hours_form.save()
            container_form.save()
            protocol_form.save()

            messages.success(request, "Daten erfolgreich gespeichert!")

            return redirect('form_page')
        
        else: 
            print('Something is wrong!')

    else:
        emp_formset = EmployeeFormset(queryset=Employee.objects.none(), initial=initial_data)
        work_form = WorkCategoryForm()
        hours_form = WorkHoursForm()
        container_form = ContainerCountForm()
        protocol_form = ProtocollistForm()

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
    return render(request, 'data_entry/forms.html', {
        'emp_formset': emp_formset,
        'work_form': work_form,
        'hours_form': hours_form,
        'container_form': container_form,
        'protocol_form': protocol_form,
        'heute': today
    })


def views_page(request):
    selected_date = request.GET.get("date", datetime.today().strftime('%Y-%m-%d'))  # Get date from URL parameters
    # selected_date = datetime.strptime(str(datetime.today()), "%Y-%m-%d").date()

    if selected_date:
        try:
            parsed_date = datetime.strptime(selected_date, "%Y-%m-%d").date()  # Convert to date
        except ValueError:
            parsed_date = None
    else:
        parsed_date = None
        print('no parsed date!')

    # Define formsets
    EmployeeFormset = modelformset_factory(Employee, form=EmployeeForm, fields=('first_name', 'surname', 'attribut', 'work_start', 'work_end', 'break_time', 'absence'), 
                                           extra=0, can_delete=True)
    WorkCategoryFormset = modelformset_factory(WorkCategory, fields=('cleaning', 'maintenance', 'interruption'), extra=0, can_delete=True)
    WorkHoursFormset = modelformset_factory(WorkHours, form=WorkHoursForm, fields=('start_time', 'end_time'), extra=0, can_delete=True)
    ContainerCountFormset = modelformset_factory(ContainerCount, fields=('alu', 'holz', 'karton', 'magnetschrott', 'kanister'), extra=0, can_delete=True)
    ProtocollistFormset = modelformset_factory(Protocollist, form=ProtocollistForm, fields=('protocollist', ), extra=0, can_delete=True)

    # Determine the querysets based on selected date
    if parsed_date:
        employee_queryset = Employee.objects.filter(created_at__date=parsed_date)
        work_category_queryset = WorkCategory.objects.filter(created_at__date=parsed_date)
        work_hours_queryset = WorkHours.objects.filter(created_at__date=parsed_date)
        container_count_queryset = ContainerCount.objects.filter(created_at__date=parsed_date)
        protocollist_queryset = Protocollist.objects.filter(created_at__date=parsed_date)  # FIXED: Correct model
    
    if request.method == "POST":
        employee_formset = EmployeeFormset(request.POST, queryset=employee_queryset, prefix='employee')
        work_category_formset = WorkCategoryFormset(request.POST, queryset=work_category_queryset, prefix='work_category')
        work_hours_formset = WorkHoursFormset(request.POST, queryset=work_hours_queryset, prefix='work_hours')
        container_count_formset = ContainerCountFormset(request.POST, queryset=container_count_queryset, prefix='container')
        protocollist_formset = ProtocollistFormset(request.POST, queryset=protocollist_queryset, prefix='protocollist')
        # work_hours_formset.is_valid() and 
        
        
        if employee_formset.is_valid():
            print("Arbeiter gespeichert")
            employee_formset.save()
            return redirect(f"{request.path}?date={selected_date}")  
        
        if work_category_formset.is_valid():
            print("Kategorien gespeichert")
            work_category_formset.save()
            return redirect(f"{request.path}?date={selected_date}")  
        
        if work_hours_formset.is_valid():
            print("Zählerstand gespeichert")
            work_hours_formset.save()
            return redirect(f"{request.path}?date={selected_date}")  

        if container_count_formset.is_valid():
            print("Container gespeichert")
            container_count_formset.save()
            return redirect(f"{request.path}?date={selected_date}")  

        if protocollist_formset.is_valid():
            protocollist_formset.save()
            return redirect(f"{request.path}?date={selected_date}")  
        # return redirect('views_page')

        else: 
            if not employee_formset.is_valid():
                print('Employee is the problem!')
                print(employee_formset.errors)
            if not work_category_formset.is_valid():
                print('Work Category is the problem!')
                print(work_category_formset.errors)
            if not work_hours_formset.is_valid():
                print('Work Hours  is the problem!')
                print(work_hours_formset.errors)
            if not container_count_formset.is_valid():
                print('Container Count is the problem!')
                print(container_count_formset.errors)
            if not protocollist_formset.is_valid():
                print('Protocollist is the problem!')
                print(protocollist_formset.errors)

    
    elif request.method == 'DELETE':
        #WorkCategoryFormset(pk=request.DELETE['delete-id'], queryset=work_category_queryset).delete()
        print('Delete!')
        #ContainerCountFormset(pk=request.DELETE['delete-id'], queryset=container_count_queryset).delete()

    else:
        employee_formset = EmployeeFormset(queryset=employee_queryset, prefix='employee')
        work_category_formset = WorkCategoryFormset(queryset=work_category_queryset, prefix='work_category')
        work_hours_formset = WorkHoursFormset(queryset=work_hours_queryset, prefix='work_hours')
        container_count_formset = ContainerCountFormset(queryset=container_count_queryset, prefix='container')
        protocollist_formset = ProtocollistFormset(queryset=protocollist_queryset, prefix='protocollist')
        # work_hours_formset.is_valid() and 

    return render(request, 'data_entry/views.html', {
        'employee_formset': employee_formset,
        'work_category_formset': work_category_formset,
        'work_hours_formset': work_hours_formset,
        'container_count_formset': container_count_formset,
        'protocollist_formset': protocollist_formset,
        'selected_date': selected_date, 
        'heute': datetime.today().strftime('%Y-%m-%d')
    })


def dashboard_view(request):
    return render(request, "data_entry/dashboard.html")

""" 
def debug_view(request):
    apps = StatelessApp.objects.all()  # Get all registered Dash apps
    print("DEBUG: Registered Dash Apps ->", apps)  # Debugging output
    return render(request, "debug.html", {"apps": apps})

def dashboard_view(request):
    # Get all work hours data
    # employee_data = Employee.objects.all()
    # work_category_data = WorkCategory.objects.all()
    work_hours_data = WorkHours.objects.all()
    # container_count_data = ContainerCount.objects.all()
    # protocollist_data = Protocollist.objects.all()

    selected_start_date = request.GET.get("start_date")
    selected_end_date = request.GET.get("end_date")

    # Convert to DataFrame
    df = pd.DataFrame.from_records(work_hours_data.values("created_at", "start_time", "end_time"))

    # Convert 'date' to datetime
    df["date"] = pd.to_datetime(df["created_at"], utc=True)
    default_start = df["date"].min()
    default_end = df["date"].max()

    df["difference"] = [wh.difference for wh in work_hours_data]
    df["difference"] = df["difference"].apply(lambda x: convert_time_difference(x))
    df["difference"] = df["difference"].astype(float)  # Convert to numeric
    
     # Apply date filtering if user selected dates
    if selected_start_date and selected_end_date:
        df_filtered = df[(df["date"] >= selected_start_date) & (df["date"] <= selected_end_date)]
    else:
        df_filtered = df  # No filter applied, show all data    

    # Group data by **week or month**
    df_filtered["week"] = df_filtered["date"].dt.strftime("%Y-W%U")  # Group by week
    df_filtered["month"] = df_filtered["date"].dt.strftime("%Y-%m")  # Group by month

    weekly_data = df_filtered.groupby("week", as_index=False)["difference"].sum().reset_index(drop=True)
    monthly_data = df_filtered.groupby("month", as_index=False)["difference"].sum().reset_index(drop=True)
    weekly_data['difference'] = weekly_data['difference'].astype(float)
    monthly_data['difference'] = monthly_data['difference'].astype(float)
    
    monthly_data.columns = ["month", "Total Hours"]
    weekly_data.columns = ["week", "Total Hours"]
    
    # 🔥 **Generate Seaborn Plots**
    # def plot_to_base64(fig):
    #     buffer = io.BytesIO()
    #     fig.savefig(buffer, format="png", bbox_inches="tight")
    #     buffer.seek(0)
    #     return base64.b64encode(buffer.getvalue()).decode()

    # # Plot: Weekly Work Hours
    # plt.figure(figsize=(10, 5))
    # sns.barplot(x="week", y="difference", data=weekly_data, palette="Blues_d")
    # plt.xticks(rotation=45)
    # plt.title("Total Work Hours per Week")
    # weekly_plot = plot_to_base64(plt)

    # # Plot: Monthly Work Hours
    # plt.figure(figsize=(10, 5))
    # sns.barplot(x="month", y="difference", data=monthly_data, palette="Greens_d")
    # plt.xticks(rotation=45)
    # plt.title("Total Work Hours per Month")
    # monthly_plot = plot_to_base64(plt)

    weekly_data["Total Hours"] = pd.to_numeric(weekly_data["Total Hours"])
    monthly_data["Total Hours"] = pd.to_numeric(monthly_data["Total Hours"])
    
    print(weekly_data)
    print(monthly_data)
    # print(weekly_data["Total Hours"].tolist())  # Check actual values
    # print(weekly_data["Total Hours"].dtype) 
    # 🔥 **Create Interactive Plots with Plotly**
    weekly_fig = px.bar(weekly_data,
                        x="week",
                        y=weekly_data["Total Hours"],  
                        title="Work Hours Difference per Week", 
                        #color_continuous_scale="Blues",
                        )
    weekly_fig.update_xaxes(type="category")  
    weekly_fig.update_traces(
    text=weekly_data["Total Hours"].astype(str),  # Ensure it's string
    texttemplate="%{text} hrs",  # Show the correct values
    hovertemplate="Week: %{x} <br>Total Hours: %{y:.1f} hrs"
    )       
    weekly_fig.update_yaxes(range=[0, weekly_data["Total Hours"].max() + 5])

    monthly_fig = px.bar(monthly_data,
                         x="month",
                         y="Total Hours",  
                         title="Work Hours Difference per Month", 
                         # text=monthly_data["Total Hours"].astype(str),
                         # color_continuous_scale="Greens", 
                         )
    monthly_fig.update_xaxes(type="category")  
    
    monthly_fig.update_traces(
    texttemplate="%{text} hrs",
    hovertemplate="Month: %{x} <br>Total Hours: %{y:.1f} hrs"
    )
    monthly_fig.update_yaxes(range=[0, monthly_data["Total Hours"].max() + 5])

    # Convert plots to JSON format for HTML rendering
    weekly_plot_json = pio.to_json(weekly_fig, validate=True)
    monthly_plot_json = pio.to_json(monthly_fig, validate=True)
    # print(weekly_plot_json)

    return render(request, "data_entry/dashboard.html", {
        "weekly_plot_json": weekly_plot_json,
        "monthly_plot_json": monthly_plot_json,
        "start_date": selected_start_date if selected_start_date else default_start,
        "end_date": selected_end_date if selected_end_date else default_end,
    })

def convert_time_difference(time_str):
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours + minutes / 60  # Convert to float
    except ValueError:
        return 0.0  # Default in case of an error """