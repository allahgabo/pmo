from django.contrib import admin
from .models import UserProfile, ActivityLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'email_notifications', 'created_at']
    list_filter = ['role', 'email_notifications']
    search_fields = ['user__username', 'user__email', 'department']
    readonly_fields = ['created_at', 'updated_at', 'projects_assigned', 'tasks_completed']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'timestamp', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
