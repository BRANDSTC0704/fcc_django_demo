from django.contrib import admin
from django import forms 

# Register your models here.
from .models import KuebelSession, KuebelEintrag, KuebelArt

class KuebelEintragInlineForm(forms.ModelForm):
    class Meta:
        model = KuebelEintrag
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the "+" (add) and pencil (edit) icons
        self.fields['kuebel_art'].widget.can_add_related = False
        self.fields['kuebel_art'].widget.can_change_related = False
        self.fields['kuebel_art'].widget.can_delete_related = False
    

class KuebelEintragInline(admin.TabularInline):
    model = KuebelEintrag
    form = KuebelEintragInlineForm
    extra = 0
    site_header = "Kübel Einträge"
    fields = [
        'kuebel_art', 'waschen_h', 'waschen_count',
        'instandh_h', 'instandh_count',
        'zerlegen_h', 'zerlegen_count'
    ]

class KuebelSessionAdmin(admin.ModelAdmin):
    site_title = 'Kübel-Metadaten'
    search_fields = ['created_at']
    list_filter = ['created_at']
    list_display = ['created_at', 'name', 'user', 'comments', 'entry_count']  # Customize as needed
    inlines = [KuebelEintragInline]

    @admin.display(description="Anzahl Einträge")
    def entry_count(self, obj):
        return obj.kuebel.count()

admin.site.register(KuebelSession, KuebelSessionAdmin)
admin.site.register(KuebelArt)
