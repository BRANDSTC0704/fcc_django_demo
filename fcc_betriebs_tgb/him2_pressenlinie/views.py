from django.shortcuts import render, redirect
from .models import ZeitAktivitaetTyp, StundenEingabeDetails, SchichtEingabeMitarbeiter
from him2_referenzdaten.models import Schicht
from .forms import PresseStundenEingabeForm, PresseZeitSessionForm
from datetime import date

def eingabe_view(request):
    schichten = Schicht.objects.all()
    zeittypen = ZeitAktivitaetTyp.objects.all()

    if request.method == 'POST':
        session_form = PresseZeitSessionForm(request.POST)
        data_form = PresseStundenEingabeForm(request.POST, schichten=schichten, zeittypen=zeittypen)

        if session_form.is_valid() and data_form.is_valid():
            # Save the session first
            session_instance = session_form.save(commit=False)
            session_instance.user = request.user
            session_instance.save()

            # Loop through schichten and zeittypen to save data
            for schicht in schichten:
                mitarbeiter_1 = data_form.cleaned_data.get(f"schicht_mitarbeiter_1_{schicht.id}")
                mitarbeiter_2 = data_form.cleaned_data.get(f"schicht_mitarbeiter_2_{schicht.id}")

                schicht_entry = SchichtEingabeMitarbeiter.objects.create(
                    session=session_instance,
                    schicht=schicht,
                    mitarbeiter_1=mitarbeiter_1,
                    mitarbeiter_2=mitarbeiter_2,
                )

                for zeittyp in zeittypen:
                    field_name = f"entry_{schicht.id}_{zeittyp.id}"
                    dauer = data_form.cleaned_data.get(field_name)
                    if dauer:
                        StundenEingabeDetails.objects.create(
                            schicht_eingabe=schicht_entry,
                            zeittyp=zeittyp,
                            dauer=dauer,
                        )
            return redirect('success')
    else:
        session_form = PresseZeitSessionForm()
        data_form = PresseStundenEingabeForm(schichten=schichten, zeittypen=zeittypen)
    
    return render(request, 'stunden_eingabe.html', {
        'session_form': session_form,
        'data_form': data_form,
        'schichten': schichten,
        'zeittypen': zeittypen,
    })
