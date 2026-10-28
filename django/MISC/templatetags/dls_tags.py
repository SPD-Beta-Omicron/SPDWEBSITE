from django import template
from datetime import datetime, timedelta
from ..utils import get_next_dst_change
from ..models import DayLightSavingsAlert

register = template.Library()

@register.inclusion_tag('MISC/dls_alert.html')
def dls_alert():
    """Template tag for DST alert - always shows."""
    next_change = get_next_dst_change()
    show_alert = True  # Always show
    message = ""
    
    if next_change:
        direction = "forward" if next_change.month == 3 else "back"
        message = (f"Next Daylight Saving Time: {next_change.strftime('%B %d, %Y')}. "
                  f"Clocks will move {direction} one hour!")
    else:
        message = "Daylight Saving Time information unavailable."
    
    # Check admin settings for override
    try:
        alert_settings = DayLightSavingsAlert.objects.first()
        if alert_settings:
            show_alert = alert_settings.is_active
            if alert_settings.name:
                message = alert_settings.name
    except DayLightSavingsAlert.DoesNotExist:
        pass
    
    return {
        'show_alert': show_alert,
        'message': message.replace('\n', '<br>'),
        'next_change': next_change
    }