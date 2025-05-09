from django.db import models
#from django.utils.timezone import now
#import datetime
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from him2_referenzdaten.models import PresseBallenTyp, Schicht


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
    zeit_typ = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Zeit_Typ'
        verbose_name_plural = 'Referenzdaten: Zeit_Typen'
    
    def __str__(self):
        return self.zeit_typ
    


class AbhProdTyp(models.Model):
    """Model containting types of buckets, ordered by creation. 

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    bez_abh_prod = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Abholung_Produktion'
        verbose_name_plural = 'Referenzdaten: Abholung_Produktion'
    
    def __str__(self):
        return self.bez_abh_prod

# Aktivitäten 
class Stundeneingabe(models.Model):
    """Model for time per shift. 

    Args:
        models: Django models object. 

    Returns: 
        None
    """
    class Meta:
        verbose_name = 'Erfassung Stunden'
        verbose_name_plural = 'Erfassung Stunden'

    schicht = models.ForeignKey(Schicht, on_delete=models.PROTECT) # soll immer gespeichert bleiben
    zeittyp = models.ForeignKey(ZeitAktivitaetTyp, on_delete=models.PROTECT) # soll immer gespeichert bleiben
    created_date = models.DateField(auto_now_add=True, editable=False, null=False, blank=False)
    dauer = models.FloatField(default=0)

    def __str__(self):
        return f"{self.schicht} - {self.zeittyp} ({self.dauer} Std. am {self.created_date})"

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
    schicht = models.ForeignKey(Schicht, on_delete=models.PROTECT) # kann nicht gelöscht werden, wenn Daten da 
    abh_prod = models.ForeignKey(AbhProdTyp, on_delete=models.PROTECT) # kann nicht gelöscht werden, wenn Daten da 
    ballentyp = models.ForeignKey(PresseBallenTyp, on_delete=models.PROTECT) # kann nicht gelöscht werden, wenn Daten da 
    anzahl = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.abh_prod}, {self.schicht} am {self.created_date}: {self.ballentyp}, Anzahl: {self.anzahl}"
