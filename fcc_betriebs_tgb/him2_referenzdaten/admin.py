from django.contrib import admin
from .models import KuebelArt, PresseBallenTyp, Schicht, Fahrzeug, Mitarbeiter, Betankung

# Register your models here.
admin.site.register(KuebelArt)
admin.site.register(PresseBallenTyp)
admin.site.register(Schicht)
admin.site.register(Fahrzeug)
admin.site.register(Mitarbeiter)
admin.site.register(Betankung)