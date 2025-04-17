from django.db import models
#from django.utils.timezone import now
#import datetime
#from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

# Kübelwaschen 
class KuebelSession(models.Model):
    name = models.CharField(max_length=100)  # e.g. session name or user-provided
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

class KuebelEintrag(models.Model):
    log = models.ForeignKey(KuebelSession, related_name='kuebel', on_delete=models.CASCADE)
    kuebel_art = models.CharField(max_length=100)
    waschen_h = models.FloatField(default=0)
    waschen_count = models.IntegerField(default=0)
    instandh_h = models.FloatField(default=0)
    instandh_count = models.IntegerField(default=0)
    zerlegen_h = models.FloatField(default=0)
    zerlegen_count = models.IntegerField(default=0)


#     def __str__(self):
#         return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.first_name} {self.surname}"


# class KuebelAnzahl(models.Model):
#     cleaning = models.FloatField(default=0.0, help_text="Hours spent on cleaning")
#     maintenance = models.FloatField(
#         default=0.0, help_text="Hours spent on maintenance/repair"
#     )
#     interruption = models.FloatField(
#         default=0.0, help_text="Hours of work interruption"
#     )
#     created_at = models.DateTimeField(
#         auto_now_add=True, editable=False, null=False, blank=False
#     )

#     def __str__(self):
#         return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.cleaning} {self.maintenance} {self.interruption}"


# class WorkHours(models.Model):
#     start_time = models.TimeField(default=now, null=False)
#     end_time = models.TimeField(default=now, null=False)
#     created_at = models.DateTimeField(
#         auto_now_add=True, editable=False, null=False, blank=False
#     )

#     def __str__(self):
#         return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.start_time} {self.end_time}"

#     @property
#     def difference(self):
#         """Calculate the difference between start and end time"""
#         if self.start_time and self.end_time:
#             dummy_date = datetime.datetime(2000, 1, 1).date()  # Use an arbitrary date

#             if isinstance(self.start_time, datetime.time):
#                 stime = self.start_time
#             elif isinstance(self.start_time, datetime.datetime):
#                 stime = self.start_time.time
#             else:
#                 print(type(self.start_time))
#                 stime = self.start_time

#             if isinstance(self.end_time, datetime.time):
#                 etime = self.end_time
#             elif isinstance(self.end_time, datetime.datetime):
#                 etime = self.end_time.time
#             else:
#                 print(type(self.end_time))
#                 etime = self.end_time

#             # print(type(stime))
#             # print(type(etime))

#             datetime1 = datetime.datetime.combine(dummy_date, stime)
#             datetime2 = datetime.datetime.combine(dummy_date, etime)

#             time_difference = datetime2 - datetime1
#             return str(time_difference)[:-3]  # Returns 'HH:MM' format

#         return "00:00"


# class ContainerCount(models.Model):
#     alu = models.IntegerField(
#         default=0,
#         help_text="Alu Dosen (Kübel - 8,5 kg)",
#         validators=[MinValueValidator(0)],
#     )
#     holz = models.IntegerField(
#         default=0, help_text="Holz (Container - 6 t)", validators=[MinValueValidator(0)]
#     )
#     karton = models.IntegerField(
#         default=0,
#         help_text="Karton (Container - 6 t)",
#         validators=[MinValueValidator(0)],
#     )
#     magnetschrott = models.IntegerField(
#         default=0,
#         help_text="Magnetschrott (Container - 6 t)",
#         validators=[MinValueValidator(0)],
#     )
#     kanister = models.IntegerField(
#         default=0,
#         help_text="Kanister (1 Container = 5 Ballen)",
#         validators=[MinValueValidator(0)],
#     )
#     created_at = models.DateTimeField(
#         auto_now_add=True, editable=False, null=False, blank=False
#     )

#     def __str__(self):
#         return f"{self.created_at:%d.%m.%Y %H:%M:%S} {self.alu}, {self.holz}, {self.karton}, {self.magnetschrott}, {self.kanister}"


# class Protocollist(models.Model):
#     protocollist = models.TextField(help_text="Protokollführer", default="keine Angabe")
#     created_at = models.DateTimeField(
#         auto_now_add=True, editable=False, null=False, blank=False
#     )
