from rest_framework import serializers
from .models import Project, Risk, Task, Resource, Milestone


class RiskSerializer(serializers.ModelSerializer):
    risk_score = serializers.ReadOnlyField()
    
    class Meta:
        model = Risk
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    
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
    health_score = serializers.ReadOnlyField()
    is_overbudget = serializers.ReadOnlyField()
    is_behind_schedule = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    total_risks = serializers.SerializerMethodField()
    high_risks = serializers.SerializerMethodField()
    
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
    health_score = serializers.ReadOnlyField()
    is_overbudget = serializers.ReadOnlyField()
    is_behind_schedule = serializers.ReadOnlyField()
    budget_variance = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    risks = RiskSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    
    total_risks = serializers.SerializerMethodField()
    high_risks = serializers.SerializerMethodField()
    open_tasks = serializers.SerializerMethodField()
    overdue_tasks = serializers.SerializerMethodField()
    
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
