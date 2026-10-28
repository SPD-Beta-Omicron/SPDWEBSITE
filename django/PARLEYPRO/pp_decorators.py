from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from AUTHENTICATE.models import Brother_Profile

def requires_role(*role_names):
    """
    Decorator that checks if a user has ALL of the specified roles.
    If not, redirects to the previous page with an error message.
    
    Usage:
    @requires_role('EXEC', 'PLEDGE_BOARD')
    def your_view(request):
        # View logic here
        pass
    """
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
            
            try:
                brother_profile = Brother_Profile.objects.get(user=request.user)
                # Convert the ManyRelatedManager to a list of values
                user_roles = list(brother_profile.roles.values_list('name', flat=True))
                
                # Check if user has ALL of the required roles
                missing_roles = [role for role in role_names if role not in user_roles]
                
                if missing_roles:
                    missing_roles_str = "', '".join(missing_roles)
                    messages.error(
                        request, 
                        f"Access denied. You are missing the following required role{'s' if len(missing_roles) > 1 else ''}: '{missing_roles_str}'"
                    )
                    return HttpResponseRedirect(previous_page) if previous_page else redirect(fallback_url)
                    
            except Brother_Profile.DoesNotExist:
                messages.error(request, "User profile not found.")
                return HttpResponseRedirect(previous_page) if previous_page else redirect(fallback_url)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator