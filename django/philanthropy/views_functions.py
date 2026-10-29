from .models import Philanthropy_Hours_Event_and_Request
from datetime import datetime, date
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

#views def philanthropy_dashboard(request):
def get_academic_year_dates(start_year):
    """Academic year runs Jul 1 of start_year through Jun 30 of start_year+1."""
    start = date(start_year, 7, 1)
    end   = date(start_year + 1, 6, 30)
    return start, end

def get_available_academic_years(past=3):
    """Last `past` academic years, most recent first."""
    today = timezone.now().date()
    # if before July, current academic year started last year
    curr_start = today.year - 1 if today.month <= 6 else today.year
    years = [curr_start - i for i in range(past)]
    return years  # e.g. [2024, 2023, 2022]

def get_user_events_and_total_hours(request,start_date, end_date):
        user_events = Philanthropy_Hours_Event_and_Request.objects.filter(
                user=request.user,
                philanthropy_event_date__range=(start_date, end_date)
            ).order_by('-philanthropy_event_date')
            
        user_total_hours = Philanthropy_Hours_Event_and_Request.objects.filter(
                user=request.user,
                philanthropy_approval_status='approved',
                philanthropy_event_date__range=(start_date, end_date)
            ).aggregate(
                total_hours=Sum('philanthropy_event_hours')
            )['total_hours'] or 0
        return user_events, user_total_hours

def collect_philanthropy_statistics(active_brothers, start_date, end_date):
        brothers_progress = []
        total_chapter_hours = 0
        members_meeting_goal = 0

        for brother in active_brothers:
            approved_hours = Philanthropy_Hours_Event_and_Request.objects.filter(
                user=brother.user,
                philanthropy_approval_status='approved',
                philanthropy_event_date__range=(start_date, end_date)
            ).aggregate(
                total_hours=Sum('philanthropy_event_hours')
            )['total_hours'] or 0
            
            brothers_progress.append({
                'user': brother.user,
                'full_name': f"{brother.firstName} {brother.lastName}",
                'total_hours': approved_hours
            })
            
            total_chapter_hours += approved_hours
            if approved_hours >= 10:
                members_meeting_goal += 1
        
        return brothers_progress, total_chapter_hours, members_meeting_goal

# views def philanthropy_approve(request):
def philanthropy_approval_POST(request):
        if request.method == 'POST':
            event_id = request.POST.get('event_id')
            action = request.POST.get('action')
            
            try:
                event = Philanthropy_Hours_Event_and_Request.objects.get(id=event_id)
                if action == 'approve':
                    event.philanthropy_approval_status = 'approved'
                    event.philanthropy_event_approver_name = f"{request.user.brother_profile.firstName} {request.user.brother_profile.lastName}"
                    event.philanthropy_event_submission_approval_date = timezone.now()
                elif action == 'deny':
                    event.philanthropy_approval_status = 'denied'
                    event.philanthropy_event_approver_name = f"{request.user.brother_profile.firstName} {request.user.brother_profile.lastName}"
                    event.philanthropy_event_submission_approval_date = timezone.now()
                
                event.save()
                messages.success(request, f"Event successfully {'approved' if action == 'approve' else 'denied'}!")
                
            except Philanthropy_Hours_Event_and_Request.DoesNotExist:
                messages.error(request, 'Event not found')
            except Exception as e:
                messages.error(request, f'Error processing request: {str(e)}')

# view def brother_philanthropy_history(request, user_id):
def retrieve_individual_brother_history(brother, user_id):
    """
    Grabs all approved events for a brother, groups them by academic year
    (Jul 1–Jun 30), and returns a list plus lifetime total.
    """
    from .models import Philanthropy_Hours_Event_and_Request

    events = Philanthropy_Hours_Event_and_Request.objects.filter(
        user_id=user_id,
        philanthropy_approval_status='approved'
    ).order_by('-philanthropy_event_date')

    # bucket by academic year start
    ay_totals = {}
    for ev in events:
        dt = ev.philanthropy_event_date
        # if month ≤ 6, it belongs to the previous academic year
        start_year = dt.year - 1 if dt.month <= 6 else dt.year
        key = f"{start_year}-{start_year+1}"
        if key not in ay_totals:
            ay_totals[key] = {'start': start_year, 'total_hours': 0, 'events': []}
        ay_totals[key]['total_hours'] += ev.philanthropy_event_hours
        ay_totals[key]['events'].append(ev)

    # convert to list and sort descending by start_year
    academic_year_totals = sorted(
        ay_totals.values(),
        key=lambda x: x['start'],
        reverse=True
    )

    # lifetime total
    lifetime_total = sum(item['total_hours'] for item in academic_year_totals)

    return academic_year_totals, lifetime_total
