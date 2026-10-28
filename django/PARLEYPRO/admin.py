from django.contrib import admin
from .models import *
# Register your models here.
#admin.site.register(Vote_Poll)

from django.utils.html import format_html

@admin.register(Vote_Poll)
class VotePollAdmin(admin.ModelAdmin):
    list_display = (
        'Vote_Poll_Name',
        'created_by',
        'Vote_Poll_Start',
        'Vote_Poll_End',
        'Vote_Poll_Count_Yes',
        'Vote_Poll_Count_No',
        'poll_result_icon',
    )
    # Make poll_result_icon sortable using Vote_Poll_Count_Yes
    def poll_result_icon(self, obj):
        if obj.Vote_Poll_Count_Yes > obj.Vote_Poll_Count_No:
            color = 'green'
            symbol = '✔️'
            label = 'Passed'
        elif obj.Vote_Poll_Count_Yes < obj.Vote_Poll_Count_No:
            color = 'red'
            symbol = '❌'
            label = 'Failed'
        else:
            color = 'gold'
            symbol = '⚖️'
            label = 'Tied'
        return format_html('<span style="color: {};">{} {}</span>', color, symbol, label)
    poll_result_icon.short_description = 'Result'
    poll_result_icon.admin_order_field = 'Vote_Poll_Count_Yes'
