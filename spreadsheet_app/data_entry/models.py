from django.db import models
from django.utils.timezone import now
from datetime import timedelta, datetime


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    work_start = models.TimeField()
    work_end = models.TimeField()
    break_time = models.FloatField(help_text="Break time in hours (e.g., 0.5 for 30 min)", default=0.0)
    absence = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.first_name} {self.surname}"

class WorkCategory(models.Model):
    cleaning = models.FloatField(default=0.0, help_text="Hours spent on cleaning")
    maintenance = models.FloatField(default=0.0, help_text="Hours spent on maintenance/repair")
    interruption = models.FloatField(default=0.0, help_text="Hours of work interruption")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.cleaning} {self.maintenance} {self.interruption}"


class WorkHours(models.Model):
    start_time = models.TimeField(default=now)
    end_time = models.TimeField(default=now)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.start_time} {self.end_time}"

    @property
    def difference(self):
        """Calculate the difference between start and end time"""
        if self.start_time and self.end_time:
            start_dt = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
            end_dt = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
            diff = end_dt - start_dt
            return diff
        return None


class Count(models.Model):
    CATEGORY_CHOICES = [
        ('Alu', 'Alu'),
        ('Holz', 'Holz'),
        ('Karton', 'Karton'),
        ('Magnetshrott', 'Magnetshrott'),
        ('Kanister', 'Kanister')
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.category}: {self.count}"

class Protocol(models.Model):
    protocollist = models.TextField()
