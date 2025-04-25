from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import KuebelSessionForm, KuebelEintragFormSet
from .models import KuebelSession, KuebelEintrag, KuebelArt
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML

def start_page(request):
    return render(request, "kuebelwaschen_him2/start_page.html")


@login_required
def kuebel_page(request):
    if request.method == 'POST':
        log_form = KuebelSessionForm(request.POST)
        formset = KuebelEintragFormSet(request.POST)

        if log_form.is_valid() and formset.is_valid():
            # Save the session log
            log = KuebelSession.objects.create(
                name=log_form.cleaned_data['name'],
                user=request.user,
                comments=log_form.cleaned_data['comments']
            )

            # Loop through each form in the formset
            for form in formset:
                if form.cleaned_data:
                    kuebel_art_value = form.cleaned_data['kuebel_art']

                    # If it's a string (e.g., due to read-only rendering), fetch the instance
                    if isinstance(kuebel_art_value, str):
                        kuebel_art_instance = KuebelArt.objects.get(name=kuebel_art_value)
                    else:
                        kuebel_art_instance = kuebel_art_value

                    # Skip saving if all the work values are 0 or empty
                    fields_to_check = [
                        'sonstiges_h', 'reinigung_h', 
                        'waschen_h', 'waschen_count',
                        'instandh_h', 'instandh_count',
                        'zerlegen_h', 'zerlegen_count'
                    ]

                    # Check if all relevant fields are zero or empty
                    if all(
                        not form.cleaned_data.get(field) or form.cleaned_data.get(field) == 0
                        for field in fields_to_check
                    ):
                        continue  # skip this form

                    # Create the entry
                    KuebelEintrag.objects.create(
                        log=log,
                        kuebel_art=kuebel_art_instance,
                        sonstiges_h=form.cleaned_data['sonstiges_h'],
                        reinigung_h=form.cleaned_data['reinigung_h'],
                        waschen_h=form.cleaned_data['waschen_h'],
                        waschen_count=form.cleaned_data['waschen_count'],
                        instandh_h=form.cleaned_data['instandh_h'],
                        instandh_count=form.cleaned_data['instandh_count'], 
                        zerlegen_h=form.cleaned_data['zerlegen_h'],
                        zerlegen_count=form.cleaned_data['zerlegen_count'], 
                    )

            print("Data saved")
            # return redirect('generate_pdf', log_id=log.id)
            # return JsonResponse({'pdf_url': reverse('generate_pdf', args=[log.id])})
            return JsonResponse({'log_id': log.id})
            # JSON response for AJAX
            # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #     return JsonResponse({'pdf_url': reverse('generate_pdf', args=[log.id])})
            # else:
            #     return redirect('generate_pdf', log.id)
        else:
            print("Form is not valid!")
    else:
        log_form = KuebelSessionForm()
        initial_data = [{'kuebel_art': art} for art in KuebelArt.objects.all()]
        formset = KuebelEintragFormSet(initial=initial_data)

    return render(request, 'kuebelwaschen_him2/kuebel_aktivitaet.html', {
        'log_form': log_form,
        'formset': formset
    })

def open_pdf_redirect(request, log_id):
    pdf_url = reverse('generate_pdf', args=[log_id])
    home_url = reverse('start_page')
    return render(request, 'kuebelwaschen_him2/open_pdf_redirect.html', {
        'pdf_url': pdf_url,
        'home_url': home_url,
    })

def home(request): 
    return HttpResponse("View is working")


def generate_pdf(request, log_id):
    log = KuebelSession.objects.get(id=log_id)
    eintraege = KuebelEintrag.objects.filter(log=log)

    html_string = render_to_string('kuebelwaschen_him2/pdf_template.html', {
        'name': log.name,
        'comments': log.comments,
        'rows': eintraege,
    })

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    return HttpResponse(pdf, content_type='application/pdf')