from django.db import models

# Day Light Savings Model
class DayLightSavingsAlert(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Day Light Savings Button Settings"
        verbose_name_plural = "Day Light Savings Button Settings"
    
    def __str__(self):
        return f"DLS Alert - Active: {self.is_active}"

# Announcements Model
class AnnouncementAlert(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title