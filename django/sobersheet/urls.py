from django.urls import path
from . import views

urlpatterns = [
    path('', views.sobersheet_dashboard, name='sobersheet_dashboard'),
    path('history/', views.sobersheet_history, name='sobersheet_history'),
    path('log/', views.sobersheet_log, name='sobersheet_log'),
    path('edit/<int:duty_id>/', views.sobersheet_edit, name='sobersheet_edit'),
    path('delete/<int:duty_id>/', views.sobersheet_delete, name='sobersheet_delete'),
    path('brother/<int:user_id>/', views.brother_sobersheet_history, name='brother_sobersheet_history'),
    path('picker/', views.sobersheet_picker, name='sobersheet_picker'),
]
