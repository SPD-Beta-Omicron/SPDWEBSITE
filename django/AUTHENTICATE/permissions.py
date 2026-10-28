"""
Role checks shared by every app.

Use has_role() inside a view to decide what to show, and @requires_role()
to block a whole view. Role names must match Role.ROLE_CHOICES in models.py;
a misspelled name raises an error instead of silently returning False.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Brother_Profile, Role

VALID_ROLES = {code for code, _ in Role.ROLE_CHOICES}


def _validate(role_names):
    unknown = [name for name in role_names if name not in VALID_ROLES]
    if unknown:
        raise ValueError(f"Unknown role name(s): {unknown}. Valid roles are listed in Role.ROLE_CHOICES.")


def get_user_roles(user):
    """Return the set of role names the user has (empty if they have no profile)."""
    if not user.is_authenticated:
        return set()
    try:
        return set(user.brother_profile.roles.values_list('name', flat=True))
    except Brother_Profile.DoesNotExist:
        return set()


def has_role(user, role_name):
    """Check if user has a specific role"""
    _validate([role_name])
    return role_name in get_user_roles(user)


def requires_role(*role_names):
    """
    Decorator that checks if a user has ALL of the specified roles.
    If not, redirects to the previous page with an error message.

    Usage:
    @requires_role('EXEC', 'NM_BOARD')
    def your_view(request):
        # View logic here
        pass
    """
    _validate(role_names)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to access this page.")
                return redirect('login')

            # Get the previous page URL
            previous_page = request.META.get('HTTP_REFERER')
            # Default fallback if no referrer is available
            fallback_url = 'poll'

            if not Brother_Profile.objects.filter(user=request.user).exists():
                messages.error(request, "User profile not found.")
                return HttpResponseRedirect(previous_page) if previous_page else redirect(fallback_url)

            user_roles = get_user_roles(request.user)

            # Check if user has ALL of the required roles
            missing_roles = [role for role in role_names if role not in user_roles]

            if missing_roles:
                missing_roles_str = "', '".join(missing_roles)
                messages.error(
                    request,
                    f"Access denied. You are missing the following required role{'s' if len(missing_roles) > 1 else ''}: '{missing_roles_str}'"
                )
                return HttpResponseRedirect(previous_page) if previous_page else redirect(fallback_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
