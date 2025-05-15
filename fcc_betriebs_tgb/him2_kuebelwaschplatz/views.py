from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import KuebelSessionForm, KuebelEintragFormSet, BetankungFormSet
from .models import KuebelSession, KuebelEintrag, KuebelArt
from him2_referenzdaten.models import Betankung, Fahrzeug
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponseRedirect
from datetime import datetime, timedelta, time
from django.templatetags.static import static


@login_required
def kuebel_page(request):
    """Links the model to the form page. Both, the session as the detailed buckets are displayed.
    A prefilled list is generated based on kuebel-types.

    Args:
        request (HttpRequest): a created request object.

    Returns:
        view: A rendered view object, including both a log-form (session) as a detailed entry formset.
    """

    fahrzeug_filter = Fahrzeug.objects.filter(bereich__icontains="Freigelände")
    initial_data = [
        {
            "fahrzeug_id": fz.id,
            "fahrzeug_name": fz.name,
        }
        for fz in fahrzeug_filter
    ]
    # print(initial_data)

    if request.method == "POST":
        log_form = KuebelSessionForm(request.POST)
        formset = KuebelEintragFormSet(request.POST)
        tank_form = BetankungFormSet(request.POST)
        print("POST DATA:", request.POST)

        if log_form.is_valid() and formset.is_valid() and tank_form.is_valid():
            # Save the session log
            log = KuebelSession.objects.create(
                mitarbeiter=log_form.cleaned_data["mitarbeiter"],
                user=request.user,
                comments=log_form.cleaned_data["comments"],
            )

            if tank_form.is_valid():
                for form in tank_form:
                    print("Form cleaned_data:", form.cleaned_data)
                for form in tank_form:
                    if not form.cleaned_data:
                        continue

                    fahrzeug_id = form.cleaned_data["fahrzeug_id"]
                    user = request.user
                    amount_fuel = form.cleaned_data["amount_fuel"]
                    hour = form.cleaned_data.get("laufzeit_hour")
                    minute = form.cleaned_data.get("laufzeit_minute")

                    if not fahrzeug_id or not amount_fuel:
                        continue

                    laufzeit = (
                        timedelta(hours=int(hour), minutes=int(minute))
                        if hour and minute
                        else None
                    )
                    if amount_fuel > 0:
                        if hour is not None and minute is not None:
                            laufzeit = timedelta(hours=int(hour), minutes=int(minute))

                    if amount_fuel:
                        Betankung.objects.create(
                            fahrzeug_id=fahrzeug_id,
                            user=user,
                            amount_fuel=amount_fuel,
                            laufzeit=laufzeit,
                            daten_eingabe_von="Kübelwaschplatz",  # or however you're setting it
                        )

            else:
                tank_form = BetankungFormSet(initial=initial_data)

            # Loop through each form in the formset
            for form in formset:
                if form.cleaned_data:

                    kuebel_art_value = form.cleaned_data["kuebel_art"]

                    if isinstance(kuebel_art_value, str):
                        kuebel_art_instance = KuebelArt.objects.get(
                            name=kuebel_art_value
                        )
                    else:
                        kuebel_art_instance = kuebel_art_value

                    # Skip saving if all the work values are 0 or empty
                    fields_to_check = [
                        "sonstiges_h",
                        "reinigung_h",
                        "waschen_h",
                        "waschen_count",
                        "instandh_h",
                        "instandh_count",
                        "zerlegen_h",
                        "zerlegen_count",
                    ]

                    # Check if all relevant fields are zero or empty
                    if all(
                        not form.cleaned_data.get(field)
                        or form.cleaned_data.get(field) == 0
                        for field in fields_to_check
                    ):
                        continue  # skip this form

                    # Create the entry
                    KuebelEintrag.objects.create(
                        log=log,
                        kuebel_art=kuebel_art_instance,
                        reinigung_h=form.cleaned_data["reinigung_h"],
                        waschen_h=form.cleaned_data["waschen_h"],
                        waschen_count=form.cleaned_data["waschen_count"],
                        instandh_h=form.cleaned_data["instandh_h"],
                        instandh_count=form.cleaned_data["instandh_count"],
                        zerlegen_h=form.cleaned_data["zerlegen_h"],
                        zerlegen_count=form.cleaned_data["zerlegen_count"],
                    )

            print("Data saved")

            # Prepare the response data with log_id and tank_id if tank was saved
            response_data = {"log_id": log.id}

            # Return the JSON response
            return JsonResponse(response_data)
            # return redirect('generate_pdf', log_id=log.id)

        else:
            print("Form is not valid!")
            print("log_form errors:", log_form.errors)
            print("formset errors:", formset.errors)
            print("tank_form errors:", tank_form.errors)

    else:
        log_form = KuebelSessionForm()
        tank_form = BetankungFormSet(initial=initial_data)
        initial_data = [{"kuebel_art": art} for art in KuebelArt.objects.all()]
        formset = KuebelEintragFormSet(initial=initial_data)

    return render(
        request,
        "him2_kuebelwaschplatz/kuebel_aktivitaet.html",
        {"log_form": log_form, "formset": formset, "tank_form": tank_form},
    )


def open_pdf_redirect(request, log_id):
    """Function to create the pdf-report and open it in a new browser tab.
    At the same time the current view is closed and the page returns to the application start page.

    Args:
        log_id (int): Session_ID for creating individual reports.

    Returns:
        view: both the pdf url and the home page.
    """
    tank_id = request.session.get("tank_id", None)  # Retrieve the tank_id from session
    # Print for debugging

    pdf_url = reverse("generate_pdf", args=[log_id])
    home_url = reverse("start_page")
    return render(
        request,
        "him2_kuebelwaschplatz/open_pdf_redirect.html",
        {
            "pdf_url": pdf_url,
            "home_url": home_url,
            "tank_id": tank_id,  # Optional: you can pass this to the template if needed
        },
    )


def generate_pdf(request, log_id):
    log = KuebelSession.objects.get(id=log_id)
    eintraege = KuebelEintrag.objects.filter(log=log)

    def print_hh_mm(td):
        total_minutes = td.total_seconds() // 60
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        return f"{hours:02d}:{minutes:02d}"

    # prepare tank data with formatted laufzeit
    tank_data = []
    if log.tank:
        tank_data.append(
            {
                "fahrzeug": log.tank.fahrzeug,
                "amount_fuel": log.tank.amount_fuel,
                "laufzeit": (
                    print_hh_mm(log.tank.laufzeit) if log.tank.laufzeit else "N/A"
                ),
            }
        )

    html_string = render_to_string(
        "him2_kuebelwaschplatz/pdf_template.html",
        {
            "mitarbeiter": log.mitarbeiter,
            "comments": log.comments,
            "rows": eintraege,
            "tank_data": tank_data,
        },
    )

    # Generate the base_url for static files
    base_url = request.build_absolute_uri("/")  # Get the base URL for static files

    # pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    pdf = HTML(string=html_string, base_url=base_url).write_pdf()
    return HttpResponse(pdf, content_type="application/pdf")


def admin_view(request):
    return HttpResponseRedirect(reverse("admin:index"))
