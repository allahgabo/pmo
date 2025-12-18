from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Project, Risk, Task, Resource, Milestone


class RiskSerializer(serializers.ModelSerializer):
    risk_score = serializers.IntegerField(read_only=True, help_text="Calculated risk score (probability * impact)")
    
    class Meta:
        model = Risk
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True, help_text="Whether the task is overdue")
    days_until_due = serializers.IntegerField(read_only=True, help_text="Number of days until due date")
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    health_score = serializers.IntegerField(read_only=True, help_text="Overall project health score (0-100)")
    is_overbudget = serializers.BooleanField(read_only=True, help_text="Whether project is over budget")
    is_behind_schedule = serializers.BooleanField(read_only=True, help_text="Whether project is behind schedule")
    days_remaining = serializers.IntegerField(read_only=True, help_text="Days remaining until project end date")
    
    total_risks = serializers.IntegerField(read_only=True, help_text="Total number of risks")
    high_risks = serializers.IntegerField(read_only=True, help_text="Number of high/critical risks")
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'status', 'priority',
            'completion_percentage', 'spi', 'cpi',
            'health_score', 'is_overbudget', 'is_behind_schedule',
            'days_remaining', 'total_risks', 'high_risks',
            'project_manager', 'start_date', 'planned_end_date'
        ]
    
    def get_total_risks(self, obj):
        return obj.risks.count()
    
    def get_high_risks(self, obj):
        return obj.risks.filter(severity__in=['high', 'critical']).count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with all related data"""
    health_score = serializers.IntegerField(read_only=True, help_text="Overall project health score (0-100)")
    is_overbudget = serializers.BooleanField(read_only=True, help_text="Whether project is over budget")
    is_behind_schedule = serializers.BooleanField(read_only=True, help_text="Whether project is behind schedule")
    budget_variance = serializers.FloatField(read_only=True, help_text="Budget variance (budget - spent)")
    days_remaining = serializers.IntegerField(read_only=True, help_text="Days remaining until project end date")
    
    risks = RiskSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    
    total_risks = serializers.IntegerField(read_only=True, help_text="Total number of risks")
    high_risks = serializers.IntegerField(read_only=True, help_text="Number of high/critical risks")
    open_tasks = serializers.IntegerField(read_only=True, help_text="Number of open tasks")
    overdue_tasks = serializers.IntegerField(read_only=True, help_text="Number of overdue tasks")
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_total_risks(self, obj):
        return obj.risks.count()
    
    def get_high_risks(self, obj):
        return obj.risks.filter(severity__in=['high', 'critical']).count()
    
    def get_open_tasks(self, obj):
        return obj.tasks.exclude(status__in=['completed', 'cancelled']).count()
    
    def get_overdue_tasks(self, obj):
        from django.utils import timezone
        return obj.tasks.filter(
            status__in=['not_started', 'in_progress'],
            due_date__lt=timezone.now().date()
        ).count()