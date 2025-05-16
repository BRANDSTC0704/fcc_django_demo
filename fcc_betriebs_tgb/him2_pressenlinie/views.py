from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    ZeitAktivitaetTyp,
    StundenEingabeDetails,
    SchichtEingabeMitarbeiter,
    Aktivitaet,
)
from him2_referenzdaten.models import Schicht, Fahrzeug, Betankung, BetankungSession
from .forms import PresseStundenEingabeForm, PresseZeitSessionForm, PresseAktivitaetForm
from him2_referenzdaten.forms import BetankungFormSet 
from datetime import timedelta 

# from datetime import date


@login_required
def eingabe_view(request):
    schichten = Schicht.objects.all()
    zeittypen = ZeitAktivitaetTyp.objects.all()

    # this is a pre-filter depending on the station 
    fahrzeug_filter = Fahrzeug.objects.filter(bereich__icontains="Presse")
    initial_data = [
        {
            "fahrzeug_id": fz.id,
            "fahrzeug_name": fz.name,
        }
        for fz in fahrzeug_filter
    ]
    
    if request.method == "POST":
        session_form = PresseZeitSessionForm(request.POST)
        data_form = PresseStundenEingabeForm(
            request.POST, schichten=schichten, zeittypen=zeittypen
        )
        aktivitaet_form = PresseAktivitaetForm(request.POST, schichten=schichten)
        tank_form = BetankungFormSet(request.POST)

        if (
            session_form.is_valid()
            and data_form.is_valid()
            and aktivitaet_form.is_valid()
            and tank_form.is_valid()
        ):

            # Save the session first - Session form
            session_instance = session_form.save(commit=False)
            session_instance.user = request.user
            session_instance.save()

            # Duration Form
            # Loop through schichten and zeittypen to save data
            for schicht in schichten:
                mitarbeiter_1 = data_form.cleaned_data.get(
                    f"schicht_mitarbeiter_1_{schicht.id}"
                )
                mitarbeiter_2 = data_form.cleaned_data.get(
                    f"schicht_mitarbeiter_2_{schicht.id}"
                )

                schicht_entry = SchichtEingabeMitarbeiter.objects.create(
                    session=session_instance,
                    schicht=schicht,
                    mitarbeiter_1=mitarbeiter_1,
                    mitarbeiter_2=mitarbeiter_2,
                )

                schicht_entry.full_clean()  # for data validation
                schicht_entry.save()

                for zeittyp in zeittypen:
                    field_name = f"entry_{schicht.id}_{zeittyp.id}"
                    dauer = data_form.cleaned_data.get(field_name)
                    if dauer:
                        StundenEingabeDetails.objects.create(
                            dauer=dauer,
                            schicht=schicht,
                            zeittyp=zeittyp,
                            session=session_instance,
                        )

                # AktivitätsForm
                strom_zaehler = aktivitaet_form.cleaned_data.get(
                    f"stromzaehler_{schicht.id}"
                )
                presse_zaehler = aktivitaet_form.cleaned_data.get(
                    f"pressezaehler_{schicht.id}"
                )

                aktivitaet_entry = Aktivitaet.objects.create(
                    session=session_instance,
                    schicht=schicht,
                    stromzaehler=strom_zaehler,
                    ballenpresse_zaehler=presse_zaehler,
                )

                aktivitaet_entry.full_clean()  # for data validation
                aktivitaet_entry.save()

                # Tankform
                if tank_form.is_valid():
                    # for form in tank_form:
                        # print("Form cleaned_data:", form.cleaned_data)
                    tank_session = None  # Prepare outside the loop

                    for form in tank_form:
                        if not form.cleaned_data:
                            continue

                        fahrzeug_id = form.cleaned_data.get("fahrzeug_id")
                        amount_fuel = form.cleaned_data.get("amount_fuel")
                        hour = form.cleaned_data.get("laufzeit_hour")
                        minute = form.cleaned_data.get("laufzeit_minute")

                        if not (amount_fuel or hour or minute):
                            continue  # skip entirely empty rows

                        # Only proceed if there is relevant input
                        laufzeit = timedelta(
                            hours=int(hour) if hour is not None else 0,
                            minutes=int(minute) if minute is not None else 0,
                        )

                        if (amount_fuel and amount_fuel > 0) or laufzeit.total_seconds() > 0:
                            # Create tank_session only once
                            if not tank_session:
                                tank_session = BetankungSession.objects.create(
                                    user=request.user,
                                    daten_eingabe_von="Kübelwaschplatz"
                                )

                            Betankung.objects.create(
                                tank_session=tank_session,
                                fahrzeug_id=fahrzeug_id,
                                amount_fuel=amount_fuel or 0,
                                laufzeit=laufzeit
                            )
                            if tank_session:
                                session_instance.tank_session = tank_session
                                session_instance.save()
                else:
                    tank_form = BetankungFormSet(initial=initial_data)
                

            return render(request, "start_page.html")
    else:
        session_form = PresseZeitSessionForm()
        data_form = PresseStundenEingabeForm(schichten=schichten, zeittypen=zeittypen)
        aktivitaet_form = PresseAktivitaetForm(schichten=schichten)
        tank_form = BetankungFormSet(initial=initial_data)
        
    return render(
        request,
        "stunden_eingabe.html",
        {
            "session_form": session_form,
            "data_form": data_form,
            "aktivitaet_form": aktivitaet_form,
            "tank_form": tank_form,
            "schichten": schichten,
            "zeittypen": zeittypen,
        },
    )
