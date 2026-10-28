import random
from datetime import date
from django.db.models import Max, Count
from AUTHENTICATE.models import Brother_Profile
from .models import Sober_Duty, Sober_Exemption


def semester_index(d):
    """Sortable integer. Fall = Jul-Dec, Spring = Jan-Jun."""
    return d.year * 2 + (1 if d.month >= 7 else 0)


def semester_label(idx):
    year, term = divmod(idx, 2)
    return f"{'Fall' if term else 'Spring'} {year}"


def build_sobersheet_queue():
    """
    Active brothers grouped by the semester of their most recent sober duty.
    Never sobered first, then oldest semester to newest.
    """
    brothers = (Brother_Profile.objects
                .filter(roles__name='ACTIVE')
                .exclude(user_id__in=get_exempt_user_ids())
                .select_related('user')
                .order_by('lastName', 'firstName'))

    stats = {
        row['user_id']: row
        for row in Sober_Duty.objects.values('user_id')
                   .annotate(last_date=Max('event_date'), total=Count('id'))
    }

    groups = {}
    for b in brothers:
        row = stats.get(b.user_id)
        idx = semester_index(row['last_date']) if row else None
        groups.setdefault(idx, []).append({
            'profile': b,
            'last_date': row['last_date'] if row else None,
            'total': row['total'] if row else 0,
        })

    ordered = sorted(groups, key=lambda i: (i is not None, i or 0))
    queue = []
    for idx in ordered:
        members = sorted(
            groups[idx],
            key=lambda m: (m['last_date'] or date.min,
                           m['profile'].lastName or '', m['profile'].firstName or '')
        )
        queue.append({
            'label': 'Never sobered' if idx is None else semester_label(idx),
            'brothers': members,
        })
    return queue


def group_history_by_event():
    """Every sober duty grouped by event (date + title), newest event first."""
    duties = (Sober_Duty.objects
              .select_related('user', 'user__brother_profile')
              .order_by('-event_date', 'event_title', 'duty_type',
                        'user__brother_profile__lastName'))
    groups = {}
    for d in duties:
        groups.setdefault((d.event_date, d.event_title), []).append(d)
    return [{'date': date, 'title': title, 'duties': duties}
            for (date, title), duties in groups.items()]


def retrieve_individual_sobersheet_history(user_id):
    """One brother's sober duties grouped by semester, newest first, plus a lifetime total."""
    duties = list(Sober_Duty.objects
                  .filter(user_id=user_id)
                  .order_by('-event_date', 'event_title'))

    groups = {}
    for d in duties:
        groups.setdefault(semester_index(d.event_date), []).append(d)

    semester_groups = [{'label': semester_label(i), 'duties': groups[i]}
                       for i in sorted(groups, reverse=True)]
    return semester_groups, len(duties)


def get_exempt_user_ids():
    """Stored exemptions plus anyone currently holding RISK_MGR (covers pre-signal data)."""
    ids = set(Sober_Exemption.objects.values_list('user_id', flat=True))
    ids |= set(Brother_Profile.objects.filter(roles__name='RISK_MGR')
               .values_list('user_id', flat=True))
    return ids


def build_exempt_list():
    brothers = (Brother_Profile.objects
                .filter(roles__name='ACTIVE', user_id__in=get_exempt_user_ids())
                .select_related('user'))

    stats = {
        row['user_id']: row
        for row in Sober_Duty.objects.values('user_id')
                   .annotate(last_date=Max('event_date'), total=Count('id'))
    }

    result = [{
        'profile': b,
        'last_date': stats[b.user_id]['last_date'] if b.user_id in stats else None,
        'total': stats[b.user_id]['total'] if b.user_id in stats else 0,
    } for b in brothers]

    # Oldest first, never sobered at the top, ties broken alphabetically
    result.sort(key=lambda m: (m['last_date'] or date.min,
                               m['profile'].lastName or '',
                               m['profile'].firstName or ''))
    return result


def pick_next_sobers(count, method):
    """
    Walk the queue from the oldest group forward. Take whole groups while they fit,
    then fill the remainder from the next group by 'random' or 'earliest'.
    """
    picked = []
    for group in build_sobersheet_queue():
        need = count - len(picked)
        if need <= 0:
            break
        members = group['brothers']
        if len(members) <= need:
            chosen = list(members)
        elif method == 'random':
            chosen = random.sample(members, need)
        else:
            chosen = sorted(
                members,
                key=lambda m: (m['last_date'] or date.min, random.random())
            )[:need]
        for m in chosen:
            picked.append({**m, 'group_label': group['label']})
    return picked