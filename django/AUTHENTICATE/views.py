from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm  # User Registration
from .forms import CreateUserForm  # User Registration

from .models import *  # Import Member from database
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import os
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .utils import contains_profanity
from NEWMEMBER.views_functions import check_user_role
from NEWMEMBER.views import newmember_dashboard

# Announcement Model
from PARLEYPRO.pp_decorators import requires_role
from MISC.models import AnnouncementAlert


from .models import DashboardLink


@login_required
def dashboard(request):
    is_new_member = check_user_role(request.user, "NEW_MEMBER")
    if is_new_member:
        return redirect("/newmember/")

    dashboard_links = DashboardLink.objects.all()
    announcements = AnnouncementAlert.objects.filter(is_active=True)
    context = {"dashboard_links": dashboard_links, "announcements": announcements}
    return render(request, "AUTHENTICATE/dashboard.html", context)


@login_required
def roster(request):
    Brother_Profiles = (
        Brother_Profile.objects.exclude(roles__name="ALUMNI")
        .order_by("lastName")
        .distinct()
    )

    # Create a mapping of PClass choices to their order for JavaScript
    pclass_order = {}
    for i, (value, label) in enumerate(PClass.choices, 1):
        pclass_order[value] = i

    context = {"Brother_Profiles": Brother_Profiles, "pclass_order": pclass_order}
    return render(request, "AUTHENTICATE/roster.html", context)


@login_required
def alumni_roster(request):
    Brother_Profiles = (
        Brother_Profile.objects.filter(roles__name="ALUMNI")
        .order_by("lastName")
        .distinct()
    )

    # Create a mapping of PClass choices to their order for JavaScript
    pclass_order = {}
    for i, (value, label) in enumerate(PClass.choices, 1):
        pclass_order[value] = i

    context = {"Brother_Profiles": Brother_Profiles, "pclass_order": pclass_order}
    return render(request, "AUTHENTICATE/roster.html", context)


def loginPage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next")
            if next_url:
                return redirect(
                    next_url
                )  # Redirect to the URL they were trying to access
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    context = {}
    return render(request, "AUTHENTICATE/login.html", context)


def logoutUser(request):
    logout(request)
    return render(request, "HOME/home.html")


@login_required
def change_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        current_password = data.get("current_password")
        new_password = data.get("new_password1")
        confirm_password = data.get("new_password2")

        user = request.user

        if not user.check_password(current_password):
            return JsonResponse(
                {"success": False, "error": "Current password is incorrect."}
            )
        elif new_password != confirm_password:
            return JsonResponse(
                {"success": False, "error": "New passwords do not match."}
            )
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
def update_profile(request):
    if request.method == "POST":
        # Get form data
        username = request.POST.get("username")
        firstname = request.POST.get("firstName")
        lastname = request.POST.get("lastName")
        hometown = request.POST.get("hometown")
        pclass = request.POST.get("pclass")  # New field

        # Check all fields for profanity
        if (
            contains_profanity(username)
            or contains_profanity(firstname)
            or contains_profanity(lastname)
            or contains_profanity(hometown)
            or contains_profanity(pclass)
        ):  # Include pclass in check
            return JsonResponse(
                {"success": False, "message": "Input contains inappropriate language."}
            )

        # Update if clean
        user = request.user
        brother_profile = Brother_Profile.objects.get(user=user)

        user.username = username
        user.email = request.POST.get("email")
        user.save()

        brother_profile.firstName = firstname
        brother_profile.lastName = lastname
        brother_profile.hometown = hometown
        brother_profile.pclass = pclass  # Save pclass field
        brother_profile.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required
def profile(request):
    brother_profile = Brother_Profile.objects.get(user=request.user)

    # Check if profile image exists and is accessible
    if brother_profile.profileImage:
        try:
            brother_profile.profileImage.url
        except:
            brother_profile.profileImage = None
            brother_profile.save()

    available_majors = Major.objects.all().order_by("name")
    context = {
        "brother_profile": brother_profile,
        "available_majors": available_majors,
        "page": "profile",
    }
    return render(request, "AUTHENTICATE/profile.html", context)


@login_required
def update_photo(request):
    if request.method == "POST" and request.FILES.get("profile_photo"):
        try:
            brother_profile = Brother_Profile.objects.get(user=request.user)

            # More detailed logging
            print(f"Processing photo upload for {request.user.username}")
            photo = request.FILES["profile_photo"]
            print(f"File name: {photo.name}")
            print(f"File size: {photo.size}")
            print(f"File content type: {photo.content_type}")

            # Delete old photo if exists and it's not the default
            if brother_profile.profileImage:
                try:
                    old_path = brother_profile.profileImage.path
                    if os.path.exists(old_path):
                        brother_profile.profileImage.delete(save=False)
                except Exception as e:
                    print(f"Error deleting old image: {e}")

            brother_profile.profileImage = request.FILES["profile_photo"]
            brother_profile.save()

            print(f"Photo saved to: {brother_profile.profileImage.path}")

            # Return JSON response for AJAX requests
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": True, "image_url": brother_profile.profileImage.url}
                )

            return HttpResponseRedirect(reverse("profile"))

        except Exception as e:
            # More detailed error logging
            print(f"ERROR in update_photo: {e}")
            import traceback

            traceback.print_exc()

            # Return more detailed error to frontend
            return JsonResponse(
                {"success": False, "message": f"{type(e).__name__}: {str(e)}"}
            )

    return HttpResponseRedirect(reverse("profile"))


@login_required
def reset_photo(request):
    if request.method == "POST":
        try:
            brother_profile = Brother_Profile.objects.get(user=request.user)
            if brother_profile.profileImage:
                # Delete the old photo file
                brother_profile.profileImage.delete()
            brother_profile.profileImage = None
            brother_profile.save()
            return JsonResponse(
                {"success": True, "message": "Profile photo reset successfully"}
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required
def update_majors(request):
    if request.method == "POST":
        data = json.loads(request.body)
        selected_majors = data.get("majors", [])

        try:
            brother_profile = Brother_Profile.objects.get(user=request.user)
            brother_profile.majors.clear()

            for major_name in selected_majors:
                major, _ = Major.objects.get_or_create(name=major_name)
                brother_profile.majors.add(major)

            return JsonResponse(
                {"success": True, "message": "Majors updated successfully"}
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


@login_required
def add_custom_major(request):
    if request.method == "POST":
        data = json.loads(request.body)
        major_name = data.get("major_name", "").strip()

        # Check for profanity
        if contains_profanity(major_name):
            return JsonResponse(
                {
                    "success": False,
                    "message": "Major name contains inappropriate language",
                }
            )

        # Capitalize each word
        major_name = " ".join(word.capitalize() for word in major_name.split())

        try:
            major, created = Major.objects.get_or_create(name=major_name)
            return JsonResponse(
                {"success": True, "major_id": major.id, "major_name": major.name}
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


# Home goes below here
