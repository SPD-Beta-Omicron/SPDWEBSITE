from django.contrib import admin
from .models import DayLightSavingsAlert, AnnouncementAlert

@admin.register(DayLightSavingsAlert)
class DayLightSavingsAlertAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'name']
    fields = ['is_active', 'name']

@admin.register(AnnouncementAlert)
class AnnouncementAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    fields = ('title', 'content')