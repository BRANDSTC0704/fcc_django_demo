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
        verbose_name_plural = 'Referenzdaten: Schicht'
    
    def __str__(self):
        return self.schichten
