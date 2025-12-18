from django.urls import path
from . import views

urlpatterns = [
    # Template views
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # API endpoints
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('api/activities/', views.ActivityLogAPIView.as_view(), name='api_activities'),
]
