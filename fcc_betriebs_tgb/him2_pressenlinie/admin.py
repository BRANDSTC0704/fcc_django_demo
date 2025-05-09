from django.contrib import admin
from django import forms 
from django.db import models
from django.forms.widgets import SelectDateWidget
from datetime import datetime

# Register your models here.
from .models import ZeitAktivitaetTyp, AbhProdTyp, Stundeneingabe, Aktivitaet, Produktion


admin.site.register(ZeitAktivitaetTyp)
admin.site.register(AbhProdTyp)
admin.site.register(Stundeneingabe)
admin.site.register(Aktivitaet)
admin.site.register(Produktion)



# class KuebelSessionAdminForm(forms.ModelForm):
#     #dat_format = '[dd.mm.yyyy hh:mm:ss]'
#     #created_at_override = forms.DateTimeField(label="erstellt am "+dat_format)

#     created_at_date = forms.DateField(
#         label="erstellt am [Datum]",
#         # widget=SelectDateWidget()
#         widget=forms.DateInput(attrs={'type': 'date'})
#     )
#     created_at_time = forms.TimeField(
#         label="erstellt am (Uhrzeit [hh:mm])",
#         widget=forms.TimeInput(format='%H:%M')
#     )

#     class Meta:
#         model = KuebelSession
#         fields = ['created_at_date', 'created_at_time', 'mitarbeiter', 'user', 'comments']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
       
#         created_at = self.instance.created_at if self.instance and self.instance.pk else datetime.now()
        
#         self.fields['created_at_date'].initial = created_at.strftime('%Y-%m-%d') # created_at.date()
#         self.fields['created_at_time'].initial = created_at.time().replace(second=0, microsecond=0)            
        
#         # self.fields['created_at_override'].initial = self.instance.created_at
#         # self.fields['created_at_date'] = forms.DateField(widget=SelectDateWidget(), label="Datum")
#         # self.fields['created_at_time'] = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), label="Zeit [HH:MM]")
        
#         self.fields['user'].label = "User (angelegt im System)"

#     def save(self, commit=True):
#         obj = super().save(commit=False)
#         date = self.cleaned_data['created_at_date']
#         time = self.cleaned_data['created_at_time']
#         obj.created_at = datetime.combine(date, time)
#         if commit:
#             obj.save()
#         return obj


# class KuebelEintragInlineForm(forms.ModelForm):
#     class Meta:
#         model = KuebelEintrag
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Remove the "+" (add) and pencil (edit) icons
#         self.fields['kuebel_art'].widget.can_add_related = False
#         self.fields['kuebel_art'].widget.can_change_related = False
#         self.fields['kuebel_art'].widget.can_delete_related = False
    

# class KuebelEintragInline(admin.TabularInline):
#     model = KuebelEintrag
#     form = KuebelEintragInlineForm
#     extra = 0
#     site_header = "Kübel Einträge"
#     fields = [
#         'kuebel_art', 'waschen_h', 'waschen_count',
#         'instandh_h', 'instandh_count',
#         'zerlegen_h', 'zerlegen_count'
#     ]

# class KuebelSessionAdmin(admin.ModelAdmin):
    
#     form = KuebelSessionAdminForm
    
#     site_title = 'Kübel-Metadaten'
#     search_fields = ['created_at']
#     list_filter = ['created_at']
#     list_display = ['mitarbeiter', 'user', 'comments', 'entry_count'] 
#     fields = ['created_at_date', 'created_at_time', 'mitarbeiter', 'user', 'comments']  
#     readonly_fields = ['entry_count']
#     inlines = [KuebelEintragInline]

#     @admin.display(description="Anzahl Einträge")
#     def entry_count(self, obj):
#         return obj.kuebel.count()

# admin.site.register(KuebelSession, KuebelSessionAdmin)
# admin.site.register(KuebelArt)
