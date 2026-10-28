from django.shortcuts import render,redirect
from AUTHENTICATE.models import * # Import Member from database
from PARLEYPRO.pp_decorators import requires_role
from MISC.models import AnnouncementAlert
from .models import BannerImage, RushFormLink, RushSlide

# SPD AUTHENTICATE
def home(request):
  Brother_Profiles = Brother_Profile.objects.all()
  banner_image = BannerImage.objects.first()
  rush_form_link = RushFormLink.objects.first()
  return render(request, 'HOME/home.html', {'Brother_Profiles': Brother_Profiles, 'banner_image': banner_image, 'rush_form_link': rush_form_link})

# Create your views here.
def ourHistory(request):
    # Count profiles that have the 'ACTIVE' role.
    num_actives = Brother_Profile.objects.filter(roles__name='ACTIVE').distinct().count()
    context = {
        'num_actives': num_actives,
    }
    return render(request, 'HOME/ourHistory.html', context)

def codeOfEthics(request):
  return render(request, 'HOME/codeOfEthics.html')

from .models import RushFormLink

def rush(request):
  rush_form_link = RushFormLink.objects.first()
  rush_slides = RushSlide.objects.all()
  return render(request, 'HOME/rush.html', {'rush_form_link': rush_form_link, 'rush_slides': rush_slides})

def executive_board(request):
    # Define a desired display order for executive roles
    exec_role_order = [
        ('PRESIDENT', 'President'),
        ('INT_VP', 'Internal Vice President'),
        ('EXT_VP', 'External Vice President'),
        ('AFFAIRS_DIRECTOR', 'Director of Chapter Affairs'),
        ('BUSINESS_MGR', 'Director of Business'),
        ('RECRUITMENT_CHAIR', 'Director of Recruitment'),
        ('PHIL_CHAIR', 'Director of Philanthropy'),
        ('RISK_MGR', 'Director of Risk Management'),
        ('SOCIAL_CHAIR', 'Director of Social Affairs'),
    ]

    brothers_by_position = []

    for role_code, role_display in exec_role_order:
        role = Role.objects.filter(name=role_code).first()
        if role:
            brothers = Brother_Profile.objects.filter(roles=role)
            for brother in brothers:
                brother.position = role_display
                brothers_by_position.append((role_display, brother))

    context = {
        'exec_board_brothers': brothers_by_position,
        'page_title': 'Executive Board',
    }
    return render(request, 'HOME/executive_board.html', context)