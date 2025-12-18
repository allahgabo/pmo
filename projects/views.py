from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from .models import Project, Risk, Task, Resource, Milestone
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    RiskSerializer, TaskSerializer, ResourceSerializer, MilestoneSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project_manager']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'status', 'completion_percentage', 'spi', 'start_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        total_projects = Project.objects.count()
        
        stats = {
            'total_projects': total_projects,
            'by_status': {
                'on_track': Project.objects.filter(status='on_track').count(),
                'at_risk': Project.objects.filter(status='at_risk').count(),
                'delayed': Project.objects.filter(status='delayed').count(),
                'completed': Project.objects.filter(status='completed').count(),
                'cancelled': Project.objects.filter(status='cancelled').count(),
            },
            'by_priority': {
                'low': Project.objects.filter(priority='low').count(),
                'medium': Project.objects.filter(priority='medium').count(),
                'high': Project.objects.filter(priority='high').count(),
                'critical': Project.objects.filter(priority='critical').count(),
            },
            'performance': {
                'projects_behind_schedule': Project.objects.filter(spi__lt=0.9).count(),
                'projects_overbudget': Project.objects.filter(spent__gt=F('budget')).count(),
                'avg_completion': round(Project.objects.aggregate(
                    avg=Avg('completion_percentage')
                )['avg'] or 0, 2),
                'avg_spi': round(Project.objects.aggregate(avg=Avg('spi'))['avg'] or 0, 2),
                'avg_cpi': round(Project.objects.aggregate(avg=Avg('cpi'))['avg'] or 0, 2),
            },
            'risks': {
                'total_risks': Risk.objects.count(),
                'high_risks': Risk.objects.filter(severity__in=['high', 'critical']).count(),
                'open_risks': Risk.objects.filter(status='open').count(),
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def at_risk_projects(self, request):
        projects = Project.objects.filter(
            Q(status__in=['at_risk', 'delayed']) |
            Q(spi__lt=0.9) |
            Q(cpi__lt=0.9)
        ).distinct()
        
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def health_report(self, request, pk=None):
        project = self.get_object()
        
        report = {
            'project_name': project.name,
            'project_code': project.code,
            'status': project.status,
            'health_score': project.health_score,
            'completion_percentage': project.completion_percentage,
            'performance_indices': {
                'spi': float(project.spi),
                'cpi': float(project.cpi),
                'is_behind_schedule': project.is_behind_schedule,
                'is_overbudget': project.is_overbudget,
            },
            'budget': {
                'total': float(project.budget),
                'spent': float(project.spent),
                'variance': project.budget_variance,
            },
            'timeline': {
                'start_date': project.start_date,
                'planned_end_date': project.planned_end_date,
                'days_remaining': project.days_remaining,
            },
            'risks': {
                'total': project.risks.count(),
                'by_severity': {
                    'critical': project.risks.filter(severity='critical').count(),
                    'high': project.risks.filter(severity='high').count(),
                    'medium': project.risks.filter(severity='medium').count(),
                    'low': project.risks.filter(severity='low').count(),
                },
                'open': project.risks.filter(status='open').count(),
            },
            'tasks': {
                'total': project.tasks.count(),
                'completed': project.tasks.filter(status='completed').count(),
                'in_progress': project.tasks.filter(status='in_progress').count(),
                'overdue': project.tasks.filter(
                    status__in=['not_started', 'in_progress'],
                    due_date__lt=timezone.now().date()
                ).count(),
            },
            'team': {
                'size': project.team_size,
                'resources': project.resources.filter(is_active=True).count(),
            }
        }
        
        return Response(report)


class RiskViewSet(viewsets.ModelViewSet):
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'category', 'severity', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['severity', 'probability', 'identified_date']
    ordering = ['-severity', '-probability']
    
    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        risks = self.queryset.filter(severity__in=['high', 'critical'], status='open')
        serializer = self.get_serializer(risks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'assigned_to', 'is_milestone']
    search_fields = ['name', 'description']
    ordering_fields = ['due_date', 'status', 'completion_percentage']
    ordering = ['due_date']
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        tasks = self.queryset.filter(
            status__in=['not_started', 'in_progress'],
            due_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'role', 'is_active']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'role', 'allocation_percentage']
    ordering = ['name']


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['planned_date', 'status']
    ordering = ['planned_date']
