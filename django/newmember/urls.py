from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.newmember_dashboard, name="newmember_dashboard"),
    path('marks/', views.newmember_marks_dashboard, name="newmember_marks_dashboard"),
    path('request/', views.newmember_request, name="newmember_request"),
    path('approve/', views.newmember_approve, name="newmember_approve"),
    path('history/<int:user_id>/', views.newmember_mark_history, name='newmember_mark_history'),
    path('export-newmember-marks/', views.export_approved_newmember_marks, name='export_newmember_marks'),
    path('edit/<int:mark_id>/', views.newmember_edit_mark, name='newmember_edit_mark'),
]
