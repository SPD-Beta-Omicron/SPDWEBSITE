from django.urls import path, re_path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('roster/', views.roster, name="roster"),
    path('alumni_roster/', views.alumni_roster, name="alumni_roster"),
    path('logout/', views.logoutUser, name="logout"),
    path('change-password/', views.change_password, name='change-password'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('update_photo/', views.update_photo, name='update_photo'),
    path('reset-photo/', views.reset_photo, name='reset_photo'),
    path('update_majors/', views.update_majors, name='update_majors'),
    path('add-custom-major/', views.add_custom_major, name='add_custom_major'),
]
