from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.philanthropy_dashboard, name="philanthropy_dashboard"),
   path('request/', views.philanthropy_request, name="philanthropy_request"),
    path('approve/', views.philanthropy_approve, name="philanthropy_approve"),
     path('brother/<int:user_id>/', views.brother_philanthropy_history, name='brother_philanthropy_history'),
     path('export-philanthropy-hours/', views.export_approved_philanthropy_hours, name='export_philanthropy_hours'),
     path('edit/<int:event_id>/', views.philanthropy_edit_event, name='philanthropy_edit_event'),
]
