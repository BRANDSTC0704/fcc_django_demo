from django.contrib import admin
from .models import Employee, WorkCategory, WorkHours, ContainerCount, Protocollist


class EmployeeAdmin(admin.ModelAdmin):
  list_display = ("created_at", "first_name", "surname", "work_start","work_end", "break_time", "absence")

# Register your models here.
# admin.site.register(Employee)
admin.site.register(WorkCategory)
admin.site.register(WorkHours)
admin.site.register(ContainerCount)
admin.site.register(Protocollist)

admin.site.register(Employee, EmployeeAdmin)