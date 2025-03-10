from django.contrib import admin
from .models import Employee, WorkCategory, WorkHours, Count, Protocol


class EmployeeAdmin(admin.ModelAdmin):
  list_display = ("created_at", "first_name", "surname", "work_start","work_end", "break_time", "absence")

# Register your models here.
# admin.site.register(Employee)
admin.site.register(WorkCategory)
admin.site.register(WorkHours)
admin.site.register(Count)
admin.site.register(Protocol)

admin.site.register(Employee, EmployeeAdmin)