from django.db import models
#from django.utils.timezone import now
#import datetime
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User ## Session User 
from him2_referenzdaten.models import PresseBallenTyp, Schicht, Mitarbeiter
from django.core.exceptions import ValidationError


# Metadaten 
class ZeitAktivitaetTyp(models.Model):
    """Model containting types of times, ordered by creation. 
    Supposed to include work-time, runtime, disturbance-time,
    maintenance-time, cleaning time. 

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Zeit_Typ'
        verbose_name_plural = 'Referenzdaten: Zeit_Typen'
    
    def __str__(self):
        return self.name
    


class AbhProdTyp(models.Model):
    """Model containting types of buckets, ordered by creation. 
    # initially: Abholung und Produktion.

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Abholung_Produktion'
        verbose_name_plural = 'Referenzdaten: Abholung_Produktion'
    
    def __str__(self):
        return self.name

# Aktivitäten 
class StundenEingabeSession(models.Model):
    """Model for time per shift. 

    Args:
        models: Django models object. 

    Returns: 
        None
    """
    class Meta:
        verbose_name = 'Erfassung Stunden'
        verbose_name_plural = 'Erfassung Stunden'

    user = models.ForeignKey(User, on_delete=models.PROTECT) # SystemUser 
    created_date = models.DateField(auto_now_add=True, editable=False, null=False, blank=False)
    created_date_mitarbeiter = models.DateField(null=False, blank=False)
    comments = models.TextField(blank=True, null=True, verbose_name='Kommentar')

    def __str__(self):
        return f"Session # {self.id} vom {self.created_date}, erstellt von {self.user}"
    
    
class SchichtEingabeMitarbeiter(models.Model):
    """Contains information on workers per Shift. 

    Args:
        models (models.Model): inherits from Django model. 
    """

    session = models.ForeignKey(StundenEingabeSession, on_delete=models.PROTECT)
    schicht = models.ForeignKey(Schicht, on_delete=models.PROTECT)
    mitarbeiter_1 = models.ForeignKey(Mitarbeiter, on_delete=models.PROTECT, related_name='+')
    mitarbeiter_2 = models.ForeignKey(Mitarbeiter, on_delete=models.PROTECT, related_name='+')
    
    def __str__(self):
        return f"Session # {self.session.id} vom {self.session.created_date}, Schicht {self.schicht} mit {self.mitarbeiter_1} und {self.mitarbeiter_2}" 

class StundenEingabeDetails(models.Model): 
    """Model for the time entry details including shift, activity type, and duration."""
    
    class Meta:
        verbose_name = 'Erfassung Stunde Detail'
        verbose_name_plural = 'Erfassung Stunden Details'
 
    session = models.ForeignKey(StundenEingabeSession, on_delete=models.PROTECT)
    schicht = models.ForeignKey(Schicht, on_delete=models.PROTECT)
    zeittyp = models.ForeignKey(ZeitAktivitaetTyp, on_delete=models.PROTECT)
    dauer = models.FloatField(default=0)  # Duration of activity

    def __str__(self):
        return f"{self.session} - {self.schicht} - {self.zeittyp} ({self.dauer} hours)"
    
    def clean(self):
        if self.schicht_mitarbeiter_1 == self.schicht_mitarbeiter_2:
            raise ValidationError("Die beiden Personen dürfen nicht gleich sein.")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Enforce the validation
        super().save(*args, **kwargs)


class Aktivitaet(models.Model):
    """Model for time per shift. 

    Args:
        models: Django models object. 

    Returns: 
        None
    """
    class Meta:
        verbose_name = 'Erfassung Aktivitäten'
        verbose_name_plural = 'Erfassung Aktivitäten'

    schicht = models.ForeignKey(Schicht, on_delete=models.PROTECT) # soll immer gespeichert bleiben
    created_date = models.DateField(auto_now_add=True, editable=False, null=False, blank=False)
    stromzaehler = models.IntegerField(default=0)
    ballenpresse_zaehler = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.schicht} am {self.created_date}: Ballenpresse - {self.ballenpresse_zaehler}, Strom: {self.stromzaehler}"


class Produktion(models.Model):
    """Modell für Ballenproduktion. 

    Args:
        models: Django models object. 

    Returns: 
        None
    """
    class Meta:
        verbose_name = 'Erfassung Ballenproduktion u. -abholung'
        verbose_name_plural = 'Erfassung Ballenproduktion u. -abholung'

    created_date = models.DateField(auto_now_add=True, editable=False, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT) # soll immer gespeichert bleiben
    mitarbeiter = models.ForeignKey(Mitarbeiter, related_name='Produktionsmitarbeiter', on_delete=models.PROTECT) # soll immer gespeichert bleiben
    schicht = models.ForeignKey(Schicht, on_delete=models.PROTECT) # kann nicht gelöscht werden, wenn Daten da 
    abh_prod = models.ForeignKey(AbhProdTyp, on_delete=models.PROTECT) # kann nicht gelöscht werden, wenn Daten da 
    ballentyp = models.ForeignKey(PresseBallenTyp, on_delete=models.PROTECT) # kann nicht gelöscht werden, wenn Daten da 
    anzahl = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.abh_prod}, {self.schicht} am {self.created_date}: {self.ballentyp}, Anzahl: {self.anzahl}"
