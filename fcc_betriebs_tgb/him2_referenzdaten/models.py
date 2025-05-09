from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
# an app containing reference data 
# Mitarbeiter
# Fuhrpark
# Ballentypen - Done 
# Containertypen - Done 
# Schicht - Done 

class KuebelArt(models.Model):
    """Model containting types of buckets, ordered by creation. 

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    kuebel_name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Behältertyp'
        verbose_name_plural = 'Referenzdaten: Behältertypen'
    
    def __str__(self):
        return self.kuebel_name


class PresseBallenTyp(models.Model):
    """Model containting types of buckets, ordered by creation. 

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    ball_name = models.CharField(max_length=100, unique=True)
    ball_gewicht = models.FloatField(default=0.5, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Ballentyp'
        verbose_name_plural = 'Referenzdaten: Ballentypen'
    
    def __str__(self):
        return  f"{self.ball_name} ({self.ball_gewicht} t)" 


class Schicht(models.Model):
    """Model containting different shifts. Initially 1, 2 and 3.. 

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    schichten = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Schicht'
        verbose_name_plural = 'Referenzdaten: Schichten'
    
    def __str__(self):
        return self.schichten


class Fahrzeug(models.Model):
    """Model containting different shifts. Initially 1, 2 and 3.. 

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    fzg_name = models.CharField(max_length=30, unique=True)
    bereich = models.CharField(max_length=30)
    kostenstelle = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Fahrzeug HIM2'
        verbose_name_plural = 'Referenzdaten: Fahrzeuge HIM2'
    
    def __str__(self):
        return f"{self.fzg_name} - {self.bereich} (KS: {self.kostenstelle}))" 
    

class Mitarbeiter(models.Model):
    """Model containting information on workers.
    Simple represantation with first and last name, function and internal/external.  

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    funktion = models.CharField(max_length=40)
    intern_extern = models.CharField(max_length=20) # über Adressbuch

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Referenzdaten: Mitarbeiter HIM2'
        verbose_name_plural = 'Referenzdaten: Mitarbeiter HIM2'
    
    def __str__(self):

        if not self.funktion: 
            return f"{self.first_name} {self.last_name}".strip()
        else: 
            return f"{self.first_name} {self.last_name} ({self.funktion})".strip() 


class Betankung(models.Model):
    """Model containting trucks and their respective tanking. Can be filled from forms within different apps. 

    Args:
        models: Django models object. 

    Returns:
        none 
    """
    fahrzeug = models.ForeignKey(Fahrzeug, verbose_name='Fahrzeug', blank=True, null=True, on_delete=models.PROTECT)
    daten_eingabe_von = models.CharField(max_length=40, verbose_name='von welcher App:') # die jeweilige App - muss beim Anlegen hard kodiert werden
    created_at = models.DateField(auto_now_add=True, editable=False, null=False, blank=False)
    amount_fuel = models.FloatField(default=0, validators=[MinValueValidator(0)], verbose_name='Diesel [l]')

    class Meta:
        ordering = ['id']  # preserves insert order
        verbose_name = 'Betankungen HIM2'
        verbose_name_plural = 'Betankungen HIM2'
    
    def __str__(self):

        return f"{self.created_at} {self.fahrzeug} {self.daten_eingabe_von} ({self.amount_fuel} l)".strip() 
