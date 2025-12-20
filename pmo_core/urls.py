from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from accounts.views import (
    dashboard_view, projects_list_view, project_detail_view, tasks_list_view,
    project_create_view, project_edit_view, project_delete_view, landing_view, ai_assistant_view
)
from projects.csv_views import (
    export_projects_csv, export_tasks_csv, export_risks_csv, export_resources_csv,
    export_all_csv, import_csv_page, import_projects_csv, data_export_page
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('', include('accounts.urls')),
    
    # Landing page and dashboard
    path('', landing_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('projects/', projects_list_view, name='projects_list'),
    path('projects/new/', project_create_view, name='project_create'),
    path('projects/<int:pk>/', project_detail_view, name='project_detail'),
    path('projects/<int:pk>/edit/', project_edit_view, name='project_edit'),
    path('projects/<int:pk>/delete/', project_delete_view, name='project_delete'),
    path('tasks/', tasks_list_view, name='tasks_list'),
    
    # AI Assistant
    path('ai-assistant/', ai_assistant_view, name='ai_assistant'),
    
    # CSV Export/Import
    path('export/', data_export_page, name='data_export_page'),
    path('export/projects/', export_projects_csv, name='export_projects_csv'),
    path('export/tasks/', export_tasks_csv, name='export_tasks_csv'),
    path('export/risks/', export_risks_csv, name='export_risks_csv'),
    path('export/resources/', export_resources_csv, name='export_resources_csv'),
    path('export/all/', export_all_csv, name='export_all_csv'),
    path('import/', import_csv_page, name='import_csv_page'),
    path('import/projects/', import_projects_csv, name='import_projects_csv'),
    
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