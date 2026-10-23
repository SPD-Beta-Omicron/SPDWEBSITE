from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from AUTHENTICATE.models import Brother_Profile
from PARLEYPRO.pp_decorators import requires_role
from .models import Sober_Duty
from .views_functions import build_sobersheet_queue, group_history_by_event, retrieve_individual_sobersheet_history, build_exempt_list, pick_next_sobers


def _is_risk_manager(user):
    return user.brother_profile.roles.filter(name='RISK_MGR').exists()


@login_required
@requires_role('ACTIVE')
def sobersheet_dashboard(request):
    context = {
        'queue_groups': build_sobersheet_queue(),
        'is_risk_manager': _is_risk_manager(request.user),
        'exempt_brothers': build_exempt_list(),
    }
    return render(request, 'sobersheet_dashboard.html', context)


@login_required
@requires_role('ACTIVE')
def sobersheet_history(request):
    context = {
        'history_groups': group_history_by_event(),
        'is_risk_manager': _is_risk_manager(request.user),
    }
    return render(request, 'sobersheet_history.html', context)

@login_required
@requires_role('ACTIVE')
def brother_sobersheet_history(request, user_id):
    try:
        brother = Brother_Profile.objects.select_related('user').get(user_id=user_id)
    except Brother_Profile.DoesNotExist:
        messages.error(request, 'Brother not found.')
        return redirect('sobersheet_dashboard')

    semester_groups, lifetime_total = retrieve_individual_sobersheet_history(user_id)
    context = {
        'brother': brother,
        'semester_groups': semester_groups,
        'lifetime_total': lifetime_total,
        'is_risk_manager': _is_risk_manager(request.user),
    }
    return render(request, 'brother_sobersheet_history.html', context)

@login_required
@requires_role('RISK_MGR')
def sobersheet_log(request):
    active = (Brother_Profile.objects.filter(roles__name='ACTIVE')
              .select_related('user').order_by('lastName', 'firstName'))

    if request.method == 'POST':
        try:
            title = request.POST['event_title'].strip()
            event_date = date.fromisoformat(request.POST['event_date'])
            duty_type = request.POST['duty_type']
            user_ids = request.POST.getlist('brothers')

            if not title:
                raise ValueError("Event title is required.")
            if duty_type not in dict(Sober_Duty.DUTY_CHOICES):
                raise ValueError("Invalid duty type.")
            if not user_ids:
                raise ValueError("Select at least one brother.")

            valid_ids = {str(b.user_id) for b in active}
            if any(uid not in valid_ids for uid in user_ids):
                raise ValueError("One or more selected brothers are not active.")

            created = 0
            for uid in user_ids:
                _, was_created = Sober_Duty.objects.get_or_create(
                    user_id=uid, event_title=title, event_date=event_date,
                    defaults={'duty_type': duty_type, 'logged_by': request.user},
                )
                created += was_created

            messages.success(request, f'Logged {created} sober duty record(s).')
            return redirect('sobersheet_dashboard')
        except Exception as e:
            messages.error(request, f'Error logging sober duty: {str(e)}')

    return render(request, 'sobersheet_log.html', {
        'brothers': active,
        'duty_choices': Sober_Duty.DUTY_CHOICES,
        'preselected': set(request.GET.getlist('brothers')),
    })


@login_required
@requires_role('RISK_MGR')
def sobersheet_edit(request, duty_id):
    duty = get_object_or_404(Sober_Duty, id=duty_id)

    if request.method == 'POST':
        try:
            title = request.POST['event_title'].strip()
            event_date = date.fromisoformat(request.POST['event_date'])
            duty_type = request.POST['duty_type']
            if not title:
                raise ValueError("Event title is required.")
            if duty_type not in dict(Sober_Duty.DUTY_CHOICES):
                raise ValueError("Invalid duty type.")

            duty.event_title = title
            duty.event_date = event_date
            duty.duty_type = duty_type
            duty.save()
            messages.success(request, 'Sober duty updated.')
            return redirect('sobersheet_history')
        except Exception as e:
            messages.error(request, f'Error updating: {str(e)}')

    return render(request, 'sobersheet_log.html', {
        'editing': True,
        'duty': duty,
        'duty_choices': Sober_Duty.DUTY_CHOICES,
    })


@login_required
@requires_role('RISK_MGR')
@require_POST
def sobersheet_delete(request, duty_id):
    duty = get_object_or_404(Sober_Duty, id=duty_id)
    duty.delete()
    messages.success(request, 'Sober duty deleted.')
    return redirect('sobersheet_history')


@login_required
@requires_role('RISK_MGR')
def sobersheet_picker(request):
    context = {'count': 2, 'method': 'earliest'}

    if request.method == 'POST':
        try:
            count = int(request.POST['count'])
            method = request.POST['method']
            if not 1 <= count <= 50:
                raise ValueError("Enter a number between 1 and 50.")
            if method not in ('random', 'earliest'):
                raise ValueError("Invalid selection method.")

            picks = pick_next_sobers(count, method)
            context.update({'count': count, 'method': method, 'picks': picks})
            if len(picks) < count:
                messages.warning(request, f'Only {len(picks)} eligible brothers exist, so fewer than {count} were returned.')
        except (ValueError, KeyError) as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'sobersheet_picker.html', context)