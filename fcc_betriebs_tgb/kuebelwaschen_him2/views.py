from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import KuebelSessionForm, KuebelEintragFormSet
from .models import KuebelSession, KuebelEintrag, KuebelArt
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML


@login_required
def kuebel_page(request):
    """Links the model to the form page. Both, the session as the detailed buckets are displayed. 
    A prefilled list is generated based on kuebel-types. 

    Args:
        request (HttpRequest): a created request object. 

    Returns:
        view: A rendered view object, including both a log-form (session) as a detailed entry formset. 
    """
    if request.method == 'POST':
        log_form = KuebelSessionForm(request.POST)
        print(log_form)
        formset = KuebelEintragFormSet(request.POST)

        if log_form.is_valid() and formset.is_valid():
            # Save the session log
            log = KuebelSession.objects.create(
                user_name_manuell=log_form.cleaned_data['user_name_manuell'],
                user=request.user,
                comments=log_form.cleaned_data['comments']
            )

            # Loop through each form in the formset
            for form in formset:
                if form.cleaned_data:
                    kuebel_art_value = form.cleaned_data['kuebel_art']

                    # If it's a string (e.g., due to read-only rendering), fetch the instance
                    if isinstance(kuebel_art_value, str):
                        kuebel_art_instance = KuebelArt.objects.get(kuebel_name=kuebel_art_value)
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
    """Function to create the pdf-report and open it in a new browser tab.
    At the same time the current view is closed and the page returns to the application start page. 

    Args:
        log_id (int): Session_ID for creating individual reports. 

    Returns:
        view: both the pdf url and the home page. 
    """
    pdf_url = reverse('generate_pdf', args=[log_id])
    home_url = reverse('start_page')
    return render(request, 'kuebelwaschen_him2/open_pdf_redirect.html', {
        'pdf_url': pdf_url,
        'home_url': home_url,
    })


def generate_pdf(request, log_id):
    """Generates a pdf from a django form. 

    Args:
        log_id (int): Session_ID. 

    Returns:
        httpResponse: a html-page that gets converted into pdf. 
    """
    log = KuebelSession.objects.get(id=log_id)
    eintraege = KuebelEintrag.objects.filter(log=log)

    html_string = render_to_string('kuebelwaschen_him2/pdf_template.html', {
        'user_name_manuell': log.user_name_manuell,
        'comments': log.comments,
        'rows': eintraege,
    })

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    return HttpResponse(pdf, content_type='application/pdf')


def admin_view(request):
    return redirect(reverse('admin:index'))