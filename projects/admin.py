from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Risk, Task, Issue, Resource, Milestone, ProjectSnapshot


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'code', 
        'name', 
        'status_badge', 
        'progress_bar',
        'health_score_badge',
        'budget_display',
        'start_date'
    ]
    list_filter = ['status', 'start_date', 'priority']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at', 'spi', 'cpi', 'health_score']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'status', 'priority')
        }),
        ('Timeline', {
            'fields': ('start_date', 'planned_end_date', 'actual_end_date', 'completion_percentage')
        }),
        ('Budget', {
            'fields': ('budget', 'spent')
        }),
        ('Performance Metrics', {
            'fields': ('spi', 'cpi', 'health_score'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'on_track': '#10b981',
            'at_risk': '#f59e0b',
            'delayed': '#ef4444',
            'completed': '#3b82f6'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progress_bar(self, obj):
        percentage = obj.completion_percentage or 0
        color = '#10b981' if percentage >= 75 else '#f59e0b' if percentage >= 50 else '#ef4444'
        return format_html(
            '<div style="width: 100px; background: #e5e7eb; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; height: 20px; text-align: center; '
            'color: white; font-size: 11px; line-height: 20px;">{:.0f}%</div></div>',
            percentage, color, percentage
        )
    progress_bar.short_description = 'Progress'
    
    def health_score_badge(self, obj):
        score = obj.health_score or 0
        if score >= 80:
            color = '#10b981'
        elif score >= 60:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 8px; font-weight: 600; font-size: 12px;">{}/100</span>',
            color, score
        )
    health_score_badge.short_description = 'Health'
    
    def budget_display(self, obj):
        if obj.budget:
            spent = obj.spent or 0
            percentage = (spent / obj.budget * 100) if obj.budget > 0 else 0
            color = '#ef4444' if percentage > 100 else '#10b981' if percentage < 90 else '#f59e0b'
            return format_html(
                '<div style="font-size: 12px;">'
                '<div style="font-weight: 600;">${:,.0f} / ${:,.0f}</div>'
                '<div style="color: {}; font-size: 11px;">{:.1f}% spent</div>'
                '</div>',
                spent, obj.budget, color, percentage
            )
        return '-'
    budget_display.short_description = 'Budget'


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'title',
        'severity_badge',
        'category',
        'probability_display',
        'impact_display',
        'status',
        'owner'
    ]
    list_filter = ['severity', 'category', 'status', 'probability', 'impact']
    search_fields = ['title', 'description', 'project__name']
    
    fieldsets = (
        ('Risk Information', {
            'fields': ('project', 'title', 'description', 'category')
        }),
        ('Assessment', {
            'fields': ('severity', 'probability', 'impact', 'status')
        }),
        ('Management', {
            'fields': ('owner', 'mitigation_plan', 'identified_date')
        })
    )
    
    def severity_badge(self, obj):
        colors = {
            'critical': '#dc2626',
            'high': '#ef4444',
            'medium': '#f59e0b',
            'low': '#10b981'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase;">{}</span>',
            colors.get(obj.severity, '#6b7280'),
            obj.severity
        )
    severity_badge.short_description = 'Severity'
    
    def probability_display(self, obj):
        value = obj.get_probability_display()
        colors = {'Very High': '#ef4444', 'High': '#f59e0b', 'Medium': '#3b82f6', 'Low': '#10b981', 'Very Low': '#6b7280'}
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 12px;">{}</span>',
            colors.get(value, '#6b7280'), value
        )
    probability_display.short_description = 'Probability'
    
    def impact_display(self, obj):
        value = obj.get_impact_display()
        colors = {'Very High': '#ef4444', 'High': '#f59e0b', 'Medium': '#3b82f6', 'Low': '#10b981', 'Very Low': '#6b7280'}
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 12px;">{}</span>',
            colors.get(value, '#6b7280'), value
        )
    impact_display.short_description = 'Impact'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'project',
        'status_badge',
        'assigned_to',
        'due_date',
        'progress_indicator'
    ]
    list_filter = ['status', 'project', 'due_date']
    search_fields = ['name', 'description', 'project__name', 'assigned_to']
    date_hierarchy = 'due_date'
    
    def status_badge(self, obj):
        colors = {
            'not_started': '#6b7280',
            'in_progress': '#3b82f6',
            'completed': '#10b981',
            'blocked': '#ef4444',
            'cancelled': '#ef4444'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progress_indicator(self, obj):
        if obj.status == 'completed':
            return format_html('<span style="color: #10b981; font-size: 18px;">✓</span>')
        elif obj.status == 'in_progress':
            return format_html('<span style="color: #3b82f6; font-size: 14px;">⏳</span>')
        elif obj.status == 'blocked':
            return format_html('<span style="color: #ef4444; font-size: 14px;">🚫</span>')
        return format_html('<span style="color: #6b7280; font-size: 14px;">○</span>')
    progress_indicator.short_description = '●'


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'title',
        'severity_badge',
        'status',
        'reported_by',
        'reported_date',
        'resolved_date'
    ]
    list_filter = ['severity', 'status', 'reported_date']
    search_fields = ['title', 'description', 'project__name']
    date_hierarchy = 'reported_date'
    
    def severity_badge(self, obj):
        colors = {
            'critical': '#dc2626',
            'high': '#ef4444',
            'medium': '#f59e0b',
            'low': '#3b82f6'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.severity, '#6b7280'),
            obj.severity.upper()
        )
    severity_badge.short_description = 'Severity'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'role_badge',
        'email',
        'utilization_bar',
        'hourly_rate_display'
    ]
    list_filter = ['role']
    search_fields = ['name', 'email', 'role']
    
    def role_badge(self, obj):
        colors = {
            'Project Manager': '#9333ea',
            'Developer': '#3b82f6',
            'Designer': '#ec4899',
            'QA': '#10b981',
            'Business Analyst': '#f59e0b'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.role, '#6b7280'),
            obj.role
        )
    role_badge.short_description = 'Role'
    
    def utilization_bar(self, obj):
        utilization = obj.utilization or 0
        color = '#ef4444' if utilization > 100 else '#f59e0b' if utilization > 80 else '#10b981'
        return format_html(
            '<div style="width: 120px; background: #e5e7eb; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; height: 20px; text-align: center; '
            'color: white; font-size: 11px; line-height: 20px; font-weight: 600;">{:.0f}%</div></div>',
            min(utilization, 100), color, utilization
        )
    utilization_bar.short_description = 'Utilization'
    
    def hourly_rate_display(self, obj):
        if obj.hourly_rate:
            return format_html(
                '<span style="font-weight: 600; color: #10b981;">${}/hr</span>',
                obj.hourly_rate
            )
        return '-'
    hourly_rate_display.short_description = 'Rate'


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'name',
        'status_badge',
        'planned_date',
        'actual_date'
    ]
    list_filter = ['status', 'project', 'planned_date']
    search_fields = ['name', 'description', 'project__name']
    date_hierarchy = 'planned_date'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#6b7280',
            'achieved': '#10b981',
            'missed': '#ef4444',
            'at_risk': '#f59e0b'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ProjectSnapshot)
class ProjectSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'snapshot_date',
        'health_score_badge',
        'completion_bar',
        'budget_status'
    ]
    list_filter = ['snapshot_date', 'project']
    search_fields = ['project__name', 'project__project_code']
    date_hierarchy = 'snapshot_date'
    readonly_fields = ['snapshot_date', 'created_at']
    
    def health_score_badge(self, obj):
        score = obj.health_score or 0
        color = '#10b981' if score >= 80 else '#f59e0b' if score >= 60 else '#ef4444'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 8px; font-weight: 600;">{}/100</span>',
            color, score
        )
    health_score_badge.short_description = 'Health'
    
    def completion_bar(self, obj):
        percentage = obj.completion_percentage or 0
        return format_html(
            '<div style="width: 100px; background: #e5e7eb; border-radius: 4px;">'
            '<div style="width: {}%; background: #3b82f6; height: 16px; '
            'text-align: center; color: white; font-size: 10px; line-height: 16px;">{:.0f}%</div></div>',
            percentage, percentage
        )
    completion_bar.short_description = 'Progress'
    
    def budget_status(self, obj):
        if obj.budget and obj.spent:
            percentage = (obj.spent / obj.budget * 100) if obj.budget > 0 else 0
            color = '#ef4444' if percentage > 100 else '#10b981'
            return format_html(
                '<span style="color: {}; font-weight: 600; font-size: 12px;">{:.1f}%</span>',
                color, percentage
            )
        return '-'
    budget_status.short_description = 'Budget %'


# Customize admin site headers
admin.site.site_header = "PMO AI Assistant Administration"
admin.site.site_title = "PMO Admin"
admin.site.index_title = "Project Management Office Dashboard"