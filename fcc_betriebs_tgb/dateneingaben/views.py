from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import KuebelSessionForm, KuebelEintragFormSet
from .models import KuebelSession, KuebelEintrag
from django.http import HttpResponse

@login_required
def kuebel_page(request):
    if request.method == 'POST':
        log_form = KuebelSessionForm(request.POST)
        formset = KuebelEintragFormSet(request.POST)
        if log_form.is_valid() and formset.is_valid():
            log = KuebelSession.objects.create(
                name=log_form.cleaned_data['name'],
                user=request.user,
                comments=log_form.cleaned_data['comments']
            )
            for form in formset:
                KuebelEintrag.objects.create(
                    log=log,
                    kuebel_art=form.cleaned_data['kuebel_art'],
                    waschen_h=form.cleaned_data['waschen_h'],
                    instandh_h=form.cleaned_data['instandh_h'],
                    instandh_count=form.cleaned_data['instandh_count'], 
                    zerlegen_h=form.cleaned_data['zerlegen_h'],
                    zerlegen_count=form.cleaned_data['zerlegen_count'], 
                )
            return redirect('success_page')  # or wherever you want
    else:
        log_form = KuebelSessionForm()
        formset = KuebelEintragFormSet()

    return render(request, 'dateneingaben/kuebel_aktivitaet.html', {
        'log_form': log_form,
        'formset': formset
    })

def home(request): 
    return HttpResponse("View is working")