from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from projects.models import Project, Task, Risk, Resource, Milestone
from accounts.models import ActivityLog


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard with portfolio overview"""
    
    # Portfolio Summary
    total_projects = Project.objects.count()
    active_projects = Project.objects.exclude(status='completed').count()
    
    status_breakdown = {
        'on_track': Project.objects.filter(status='on_track').count(),
        'at_risk': Project.objects.filter(status='at_risk').count(),
        'delayed': Project.objects.filter(status='delayed').count(),
        'completed': Project.objects.filter(status='completed').count(),
    }
    
    # Performance Metrics
    avg_completion = Project.objects.aggregate(avg=Avg('completion_percentage'))['avg'] or 0
    avg_spi = Project.objects.aggregate(avg=Avg('spi'))['avg'] or 0
    avg_cpi = Project.objects.aggregate(avg=Avg('cpi'))['avg'] or 0
    
    # Budget Analysis
    total_budget = Project.objects.aggregate(total=Sum('budget'))['total'] or 0
    total_spent = Project.objects.aggregate(total=Sum('spent'))['total'] or 0
    budget_variance = float(total_budget) - float(total_spent)
    budget_utilization = (float(total_spent) / float(total_budget) * 100) if total_budget > 0 else 0
    
    # Risk Analysis
    total_risks = Risk.objects.count()
    risk_by_severity = {
        'critical': Risk.objects.filter(severity='critical').count(),
        'high': Risk.objects.filter(severity='high').count(),
        'medium': Risk.objects.filter(severity='medium').count(),
        'low': Risk.objects.filter(severity='low').count(),
    }
    
    # Task Analysis
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='completed').count()
    overdue_tasks = Task.objects.filter(
        status__in=['not_started', 'in_progress'],
        due_date__lt=timezone.now().date()
    ).count()
    
    # Top Projects (calculate health scores in Python since it's a property)
    all_active_projects = Project.objects.exclude(status='completed')
    projects_with_scores = []
    
    for project in all_active_projects:
        projects_with_scores.append({
            'project': project,
            'health_score': project.health_score
        })
    
    # Sort by health score
    projects_with_scores.sort(key=lambda x: x['health_score'], reverse=True)
    
    # Get top 5 and bottom 5
    top_projects = [item['project'] for item in projects_with_scores[:5]]
    bottom_projects = [item['project'] for item in projects_with_scores[-5:]]
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'status_breakdown': status_breakdown,
        'avg_completion': round(avg_completion, 1),
        'avg_spi': round(avg_spi, 2),
        'avg_cpi': round(avg_cpi, 2),
        'total_budget': total_budget,
        'total_spent': total_spent,
        'budget_variance': budget_variance,
        'budget_utilization': round(budget_utilization, 1),
        'total_risks': total_risks,
        'risk_by_severity': risk_by_severity,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'top_projects': top_projects,
        'bottom_projects': bottom_projects,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def project_analytics(request):
    """Detailed project analytics"""
    
    projects = Project.objects.all()
    
    # Performance Distribution
    projects_by_spi = {
        'ahead': projects.filter(spi__gte=1.1).count(),
        'on_track': projects.filter(spi__gte=0.9, spi__lt=1.1).count(),
        'behind': projects.filter(spi__lt=0.9).count(),
    }
    
    # Budget projects
    budget_projects = []
    for project in projects:
        if project.budget and project.spent:
            variance = float(project.budget) - float(project.spent)
            budget_projects.append({
                'project': project,
                'variance': variance,
            })
    
    budget_projects.sort(key=lambda x: x['variance'])
    
    context = {
        'projects': projects,
        'projects_by_spi': projects_by_spi,
        'budget_projects': budget_projects[:10],
    }
    
    return render(request, 'analytics/projects.html', context)


@login_required
def risk_analytics(request):
    """Risk analysis"""
    
    risks = Risk.objects.select_related('project').all()
    
    # Risk by Category
    risk_categories = risks.values('category').annotate(count=Count('id')).order_by('-count')
    
    # Top Risks
    top_risks = risks.order_by('-risk_score')[:15]
    
    context = {
        'total_risks': risks.count(),
        'risk_categories': risk_categories,
        'top_risks': top_risks,
    }
    
    return render(request, 'analytics/risks.html', context)