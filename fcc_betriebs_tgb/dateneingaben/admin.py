from django.contrib import admin

# Register your models here.
from .models import KuebelSession, KuebelEintrag, KuebelArt

admin.site.register(KuebelSession)
admin.site.register(KuebelEintrag)
admin.site.register(KuebelArt)
