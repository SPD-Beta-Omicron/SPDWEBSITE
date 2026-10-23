from django.db import models
from django.contrib.auth.models import User


class Sober_Duty(models.Model):
    DUTY_CHOICES = [
        ('MONITOR', 'Sober Monitor'),
        ('DRIVER', 'Sober Driver'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sobersheet_duties')
    event_title = models.CharField(max_length=100, help_text="Name of the event")
    event_date = models.DateField(help_text="The date of the event")
    duty_type = models.CharField(max_length=10, choices=DUTY_CHOICES)
    logged_by = models.ForeignKey(
        User, related_name='logged_sobersheet_duties',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_title} - {self.user.username}"

    class Meta:
        verbose_name = "Sober Duty"
        verbose_name_plural = "Sober Duties"
        ordering = ['-event_date']

class Sober_Exemption(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sobersheet_exemption')
    reason = models.CharField(max_length=100, default='Former Risk Manager')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.reason})"

    class Meta:
        verbose_name = "Sober Exemption"
        verbose_name_plural = "Sober Exemptions"