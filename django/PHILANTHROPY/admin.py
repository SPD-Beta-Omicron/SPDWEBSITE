from django.contrib import admin
from .models import *

# Register your models here.

#admin.site.register(Philanthropy_Hours_Event_and_Request)

@admin.register(Philanthropy_Hours_Event_and_Request)
class PhilanthropyHoursEventAndRequestAdmin(admin.ModelAdmin):
    list_display = (
        'philanthropy_event_title',
        'user',
        'philanthropy_approval_status',
        'philanthropy_event_hours',
        'philanthropy_event_date',
    )
