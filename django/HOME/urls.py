from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ourHistory/', views.ourHistory, name='ourHistory'),
    path('rush/', views.rush, name='rush'),
    path('codeOfEthics/', views.codeOfEthics, name='codeOfEthics'),
    path('executive-board/', views.executive_board, name='executive_board'),
]