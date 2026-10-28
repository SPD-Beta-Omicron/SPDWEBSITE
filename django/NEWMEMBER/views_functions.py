from .models import NewMember_Mark_Event_and_Request
from AUTHENTICATE.models import Brother_Profile
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from django.contrib import messages
from django.shortcuts import redirect

def get_new_members():
    """Get all users with NEW_MEMBER role, ordered by last name"""
    return (
        Brother_Profile.objects
        .filter(roles__name="NEW_MEMBER")
        .select_related("user")
        .order_by("lastName")
        .distinct()
    )

def calculate_member_marks(new_members, start_date=None, end_date=None):
    """Calculate marks for each new member within date range"""
    new_members_progress = []
    
    for member in new_members:
        marks_query = NewMember_Mark_Event_and_Request.objects.filter(
            target_user=member.user,
            mark_approval_status='approved'
        )
        
        if start_date and end_date:
            marks_query = marks_query.filter(mark_event_date__range=(start_date, end_date))
            
        approved_marks = marks_query.aggregate(
            total_marks=Sum('mark_value')
        )['total_marks'] or 0
        
        new_members_progress.append({
            'user': member.user,
            'full_name': f"{member.firstName} {member.lastName}",
            'total_marks': approved_marks,
            'is_negative': approved_marks < 0
        })
    
    return sorted(new_members_progress, key=lambda x: x['total_marks'])


from django.db.models import Q

def get_user_submitted_marks(user, start_date=None, end_date=None):
    """Get marks submitted by a specific user within date range, excluding approved marks"""
    # Get the date one month ago
    one_month_ago = timezone.now() - timedelta(days=14)

    marks_query = NewMember_Mark_Event_and_Request.objects.filter(
        requesting_user=user,
        mark_approval_status__in=['requested', 'denied']
    )
    
    # Filter out denied marks older than one month
    marks_query = marks_query.filter(
        ~(
            Q(mark_approval_status='denied') & Q(mark_event_date__lt=one_month_ago)
        )
    )
    
    if start_date and end_date:
        marks_query = marks_query.filter(mark_event_date__range=(start_date, end_date))
        
    return marks_query.order_by('-mark_event_date')

def get_personal_stats(user):
    """Calculate personal statistics for a new member"""
    personal_marks = NewMember_Mark_Event_and_Request.objects.filter(
        target_user=user,
        mark_approval_status='approved'
    )
    
    total_marks = personal_marks.aggregate(Sum('mark_value'))['mark_value__sum'] or 0
    latest_mark = personal_marks.order_by('-mark_event_date').first()
    
    # Calculate class average
    new_members = get_new_members()
    all_member_marks = {}
    for member in new_members:
        member_total = NewMember_Mark_Event_and_Request.objects.filter(
            target_user=member.user,
            mark_approval_status='approved'
        ).aggregate(Sum('mark_value'))['mark_value__sum'] or 0
        all_member_marks[member.user.id] = member_total
    
    class_average = sum(all_member_marks.values()) / len(all_member_marks) if all_member_marks else 0
    
    return {
        'total_marks': total_marks,
        'class_average': round(class_average, 1),
        'standing': 'Good Standing' if total_marks >= 0 else 'Needs Improvement',
        'latest_mark': latest_mark
    }

def get_active_member_analytics(new_members_progress):
    """Calculate analytics for active members"""
    last_week = timezone.now() - timedelta(days=7)
    
    return {
        'total_new_members': len(new_members_progress),
        'members_in_good_standing': sum(1 for m in new_members_progress if not m['is_negative']),
        'average_marks': round(sum(m['total_marks'] for m in new_members_progress) / len(new_members_progress), 1) if new_members_progress else 0,
        'marks_this_week': NewMember_Mark_Event_and_Request.objects.filter(
            mark_event_date__gte=last_week,
            mark_approval_status='approved'
        ).count(),
        'pending_requests': NewMember_Mark_Event_and_Request.objects.filter(
            mark_approval_status='requested'
        ).count()
    }

def create_mark_requests(requesting_user, target_users, mark_value, mark_reason, mark_date):
    """Create multiple mark requests, auto-approve if NM_BOARD"""
    try:
        is_board_member = check_user_role(requesting_user, 'NM_BOARD')
        created_marks = []
        for user_id in target_users:
            new_mark = NewMember_Mark_Event_and_Request(
                requesting_user=requesting_user,
                target_user_id=user_id,
                mark_event_title=mark_reason,
                mark_value=mark_value,
                mark_event_date=mark_date,
                mark_approval_status='approved' if is_board_member else 'requested',
                mark_submission_approval_date=timezone.now() if is_board_member else None,
                mark_approver_name=f"{requesting_user.brother_profile.firstName} {requesting_user.brother_profile.lastName}" if is_board_member else None,
            )
            created_marks.append(new_mark)
        
        NewMember_Mark_Event_and_Request.objects.bulk_create(created_marks)
        return True, f'Marks submitted successfully for {len(target_users)} new member(s)!'
    except Exception as e:
        return False, f'Error submitting marks: {str(e)}'


def process_mark_approval(request, mark_id, action):
    """Process mark approval/denial"""
    try:
        mark = NewMember_Mark_Event_and_Request.objects.get(id=mark_id)
        if action == 'approve':
            mark.mark_approval_status = 'approved'
            mark.mark_approver_name = f"{request.user.brother_profile.firstName} {request.user.brother_profile.lastName}"
            mark.mark_submission_approval_date = timezone.now()
        elif action == 'deny':
            mark.mark_approval_status = 'denied'
            mark.mark_approver_name = f"{request.user.brother_profile.firstName} {request.user.brother_profile.lastName}"
            mark.mark_submission_approval_date = timezone.now()
        
        mark.save()
        return True, f"Mark(s) successfully {'approved' if action == 'approve' else 'denied'}!"
    except NewMember_Mark_Event_and_Request.DoesNotExist:
        return False, 'Mark not found'
    except Exception as e:
        return False, f'Error processing request: {str(e)}'

def get_pending_mark_requests():
    """Get all pending mark requests with proper user relationship traversal"""
    try:
        pending_requests = NewMember_Mark_Event_and_Request.objects.filter(
            mark_approval_status='requested'
        ).select_related(
            'requesting_user',
            'requesting_user__brother_profile',
            'target_user',
            'target_user__brother_profile'
        ).order_by('-mark_event_date')
        
        return pending_requests
    except Exception as e:
        print(f"Error in get_pending_mark_requests: {str(e)}")
        return NewMember_Mark_Event_and_Request.objects.none()

def get_member_mark_history(user_id):
    """Get mark history for a specific member"""
    marks = NewMember_Mark_Event_and_Request.objects.filter(
        target_user_id=user_id,
        mark_approval_status='approved'
    ).order_by('-mark_event_date')
    
    total_marks = marks.aggregate(
        total=Sum('mark_value')
    )['total'] or 0
    
    return marks, total_marks

def check_user_role(user, role_name):
    """Check if user has a specific role"""
    return user.brother_profile.roles.filter(name=role_name).exists()