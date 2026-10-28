from django.shortcuts import render
from .utils import get_next_dst_change

def daylight_savings_alert(request):
    """View for DST alert functionality."""
    next_change = get_next_dst_change()
    
    if not next_change:
        message = 'No upcoming Daylight Saving Time changes found.'
    else:
        action = ("forward" if next_change.month == 3 else "back")
        message = (f"Daylight Saving Time is on {next_change.strftime('%B %d, %Y')}. "
                  f"Clocks will move {action} one hour!")
    
    context = {
        'message': message.replace('\n', '<br>'),
        'show_alert': True,
    }
    
    return render(request, 'MISC/dls_alert.html', context)