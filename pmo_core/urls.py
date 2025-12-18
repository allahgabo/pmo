from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from accounts.views import (
    dashboard_view, projects_list_view, project_detail_view, tasks_list_view,
    project_create_view, project_edit_view, project_delete_view
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('', include('accounts.urls')),
    
    # Dashboard and main views
    path('', dashboard_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('projects/', projects_list_view, name='projects_list'),
    path('projects/new/', project_create_view, name='project_create'),
    path('projects/<int:pk>/', project_detail_view, name='project_detail'),
    path('projects/<int:pk>/edit/', project_edit_view, name='project_edit'),
    path('projects/<int:pk>/delete/', project_delete_view, name='project_delete'),
    path('tasks/', tasks_list_view, name='tasks_list'),
    
    # Analytics
    path('analytics/', include('analytics.urls')),
    
    # API Documentation
    path('api/', TemplateView.as_view(template_name='api_docs.html'), name='api-home'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-alias'),
    
    # API Endpoints
    path('api/', include('projects.urls')),
    path('api/ai/', include('ai_engine.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)