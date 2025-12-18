from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('projects/', views.project_analytics, name='projects'),
    path('risks/', views.risk_analytics, name='risks'),
]