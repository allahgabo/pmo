from django.contrib import admin
from .models import Project, Risk, Task, Resource, Milestone


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'status', 'priority', 'completion_percentage', 'spi', 'project_manager']
    list_filter = ['status', 'priority', 'project_manager']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at', 'health_score', 'is_overbudget', 'is_behind_schedule']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'status', 'priority')
        }),
        ('Timeline', {
            'fields': ('start_date', 'planned_end_date', 'actual_end_date')
        }),
        ('Budget', {
            'fields': ('budget', 'spent')
        }),
        ('Performance', {
            'fields': ('completion_percentage', 'spi', 'cpi')
        }),
        ('Team', {
            'fields': ('project_manager', 'sponsor', 'team_size')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'health_score', 'is_overbudget', 'is_behind_schedule'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'category', 'severity', 'status', 'probability', 'risk_score']
    list_filter = ['severity', 'category', 'status', 'project']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'risk_score']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'assigned_to', 'due_date', 'completion_percentage', 'is_overdue']
    list_filter = ['status', 'is_milestone', 'is_critical_path', 'project']
    search_fields = ['name', 'description', 'assigned_to']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue', 'days_until_due']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'role', 'allocation_percentage', 'is_active']
    list_filter = ['role', 'is_active', 'project']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'planned_date', 'actual_date', 'status']
    list_filter = ['status', 'project']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
