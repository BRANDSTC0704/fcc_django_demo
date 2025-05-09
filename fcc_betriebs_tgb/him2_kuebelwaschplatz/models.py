from django.db import models
#from django.utils.timezone import now
#import datetime
#from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from him2_referenzdaten.models import KuebelArt, Mitarbeiter, Betankung

# Kübelwaschen 
class KuebelSession(models.Model):
    """Session model for form filling. Includes a link to user-registration,
    time stamp a name to be typed in as well as a comment field. 

    Args:
        models: Django models object. 

    Returns: 
        None
    """
    class Meta:
        verbose_name = 'Kübel-Tagesübersicht'
        verbose_name_plural = 'Kübel-Tagesübersichten'

    mitarbeiter = models.ForeignKey(Mitarbeiter, verbose_name='Mitarbeiter', blank=False, null=False, on_delete=models.PROTECT)  # e.g. session name or user-provided
    user = models.ForeignKey(User, on_delete=models.PROTECT) # soll immer gespeichert bleiben
    tank = models.ForeignKey(Betankung, on_delete=models.PROTECT, null=True, blank=True) 
    comments = models.TextField(blank=True, null=True, verbose_name='Kommentar')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

class KuebelEintrag(models.Model):
    """Detailed list for individual entries. Includes container counts and hours for different activities. 

    Args:
        models: Django models object.
    """
    
    class Meta:
        verbose_name = 'Kübel-Detaileintrag'
        verbose_name_plural = 'Kübel-Detaileinträge'

    log = models.ForeignKey(KuebelSession, related_name='kuebel', on_delete=models.CASCADE)
    kuebel_art = models.ForeignKey(KuebelArt, on_delete=models.PROTECT)
    sonstiges_h = models.FloatField(default=0)
    reinigung_h = models.FloatField(default=0)
    waschen_h = models.FloatField(default=0)
    waschen_count = models.IntegerField(default=0)
    instandh_h = models.FloatField(default=0)
    instandh_count = models.IntegerField(default=0)
    zerlegen_h = models.FloatField(default=0)
    zerlegen_count = models.IntegerField(default=0)