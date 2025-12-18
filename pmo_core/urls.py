from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from accounts.views import (
    dashboard_view, projects_list_view, project_detail_view, tasks_list_view
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
    path('projects/<int:pk>/', project_detail_view, name='project_detail'),
    path('tasks/', tasks_list_view, name='tasks_list'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Endpoints
    path('api/', include('projects.urls')),
    path('api/ai/', include('ai_engine.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
