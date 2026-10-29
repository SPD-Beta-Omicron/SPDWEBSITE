from django.contrib import admin
from .models import NewMember_Mark_Event_and_Request
# Register your models here.
#admin.site.register(NewMember_Mark_Event_and_Request)

@admin.register(NewMember_Mark_Event_and_Request)
class NewMemberMarkEventAndRequestAdmin(admin.ModelAdmin):
    list_display = (
        'mark_event_title',
        'target_user',
        'requesting_user',
        'mark_approval_status',
        'mark_value',
        'mark_event_date',
    )
