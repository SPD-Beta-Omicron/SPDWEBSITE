from django.db import models
from django.contrib.auth.models import User

class NewMember_Mark_Event_and_Request(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('requested', 'Requested'),
        ('denied', 'Denied'),
    ]

    requesting_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='mark_requests_made',
        help_text="The active member submitting the mark"
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='marks_received',
        help_text="The new member receiving the mark"
    )
    mark_event_title = models.CharField(max_length=100, help_text="reason for the mark")
    mark_approval_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested',
        help_text="Mark Status: approved, requested, or denied"
    )
    mark_value = models.IntegerField(help_text="Can be positive or negative")
    mark_event_date = models.DateField(help_text="The date the mark was issued")
    mark_submission_request_date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date the mark was submitted"
    )
    mark_submission_approval_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date the mark was approved/denied"
    )
    mark_approver_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="The name of the person who approved/denied the mark"
    )
    last_edited_by = models.ForeignKey(
        User, related_name="edited_marks", 
        null=True,
        blank=True, 
        on_delete=models.SET_NULL
    )
    last_edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.mark_event_title} - {self.target_user.username} ({self.mark_value})"

    class Meta:
        verbose_name = "New Member Mark Event"
        verbose_name_plural = "New Member Mark Events"
        ordering = ['-mark_event_date']
