from django.contrib import admin
from .models import Sober_Duty, Sober_Exemption


@admin.register(Sober_Duty)
class SoberDutyAdmin(admin.ModelAdmin):
    list_display = ('event_title', 'user', 'duty_type', 'event_date')
    list_filter = ('duty_type',)


@admin.register(Sober_Exemption)
class SoberExemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason', 'created_at')