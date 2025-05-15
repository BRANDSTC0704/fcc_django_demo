from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    ZeitAktivitaetTyp,
    StundenEingabeDetails,
    SchichtEingabeMitarbeiter,
    Aktivitaet,
)
from him2_referenzdaten.models import Schicht
from .forms import PresseStundenEingabeForm, PresseZeitSessionForm, PresseAktivitaetForm

# from datetime import date


@login_required
def eingabe_view(request):
    schichten = Schicht.objects.all()
    zeittypen = ZeitAktivitaetTyp.objects.all()

    if request.method == "POST":
        session_form = PresseZeitSessionForm(request.POST)
        data_form = PresseStundenEingabeForm(
            request.POST, schichten=schichten, zeittypen=zeittypen
        )
        aktivitaet_form = PresseAktivitaetForm(request.POST, schichten=schichten)

        if (
            session_form.is_valid()
            and data_form.is_valid()
            and aktivitaet_form.is_valid()
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

            return render(request, "start_page.html")
    else:
        session_form = PresseZeitSessionForm()
        data_form = PresseStundenEingabeForm(schichten=schichten, zeittypen=zeittypen)
        aktivitaet_form = PresseAktivitaetForm(schichten=schichten)

    return render(
        request,
        "stunden_eingabe.html",
        {
            "session_form": session_form,
            "data_form": data_form,
            "aktivitaet_form": aktivitaet_form,
            "schichten": schichten,
            "zeittypen": zeittypen,
        },
    )
