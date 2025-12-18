from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, F
from projects.models import Project, Risk
from projects.serializers import ProjectListSerializer
from .service import PMOAIEngine


class ProjectSummaryView(APIView):
    """
    Generate AI summary for a specific project
    """
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare project data
        project_data = {
            'name': project.name,
            'code': project.code,
            'status': project.status,
            'completion_percentage': project.completion_percentage,
            'spi': float(project.spi),
            'cpi': float(project.cpi),
            'total_risks': project.risks.count(),
            'high_risks': project.risks.filter(severity__in=['high', 'critical']).count(),
            'budget': float(project.budget),
            'spent': float(project.spent),
            'days_remaining': project.days_remaining,
            'health_score': project.health_score,
        }
        
        # Generate AI summary
        ai_engine = PMOAIEngine()
        summary = ai_engine.generate_project_summary(project_data)
        
        return Response(summary)


class PortfolioSummaryView(APIView):
    """
    Generate AI summary for the entire portfolio
    """
    def get(self, request):
        # Get portfolio statistics
        total_projects = Project.objects.count()
        
        portfolio_data = {
            'total_projects': total_projects,
            'on_track': Project.objects.filter(status='on_track').count(),
            'at_risk': Project.objects.filter(status='at_risk').count(),
            'delayed': Project.objects.filter(status='delayed').count(),
            'completed': Project.objects.filter(status='completed').count(),
            'projects_behind_schedule': Project.objects.filter(spi__lt=0.9).count(),
            'avg_completion': round(Project.objects.aggregate(
                avg=Avg('completion_percentage')
            )['avg'] or 0, 2),
            'avg_spi': round(Project.objects.aggregate(avg=Avg('spi'))['avg'] or 0, 2),
            'total_risks': Risk.objects.count(),
            'high_risks': Risk.objects.filter(severity__in=['high', 'critical']).count(),
        }
        
        # Generate AI summary
        ai_engine = PMOAIEngine()
        summary = ai_engine.generate_portfolio_summary(portfolio_data)
        
        return Response(summary)


class RiskAnalysisView(APIView):
    """
    Analyze a specific risk using AI
    """
    def get(self, request, risk_id):
        try:
            risk = Risk.objects.get(id=risk_id)
        except Risk.DoesNotExist:
            return Response(
                {'error': 'Risk not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare risk data
        risk_data = {
            'title': risk.title,
            'category': risk.category,
            'severity': risk.severity,
            'probability': risk.probability,
            'impact': risk.impact,
            'description': risk.description,
            'mitigation_plan': risk.mitigation_plan,
            'project_name': risk.project.name,
            'risk_score': risk.risk_score,
        }
        
        # Generate AI analysis
        ai_engine = PMOAIEngine()
        analysis = ai_engine.analyze_risk(risk_data)
        
        return Response(analysis)


class PMOQuestionView(APIView):
    """
    Answer a PMO question using AI
    """
    def post(self, request):
        question = request.data.get('question')
        
        if not question:
            return Response(
                {'error': 'Question is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Gather context data
        context_data = {
            'portfolio': {
                'total_projects': Project.objects.count(),
                'on_track': Project.objects.filter(status='on_track').count(),
                'at_risk': Project.objects.filter(status='at_risk').count(),
                'delayed': Project.objects.filter(status='delayed').count(),
            },
            'recent_projects': list(
                Project.objects.all()[:5].values(
                    'name', 'code', 'status', 'spi', 'completion_percentage'
                )
            )
        }
        
        # Get AI answer
        ai_engine = PMOAIEngine()
        answer = ai_engine.answer_pmo_question(question, context_data)
        
        return Response(answer)


class ProjectComparisonView(APIView):
    """
    Compare multiple projects using AI
    """
    def post(self, request):
        project_ids = request.data.get('project_ids', [])
        
        if not project_ids:
            return Response(
                {'error': 'Project IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get projects
        projects = Project.objects.filter(id__in=project_ids)
        
        if not projects.exists():
            return Response(
                {'error': 'No projects found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare project data
        projects_data = []
        for project in projects:
            projects_data.append({
                'name': project.name,
                'code': project.code,
                'status': project.status,
                'completion_percentage': project.completion_percentage,
                'spi': float(project.spi),
                'cpi': float(project.cpi),
                'health_score': project.health_score,
                'total_risks': project.risks.count(),
                'high_risks': project.risks.filter(severity__in=['high', 'critical']).count(),
            })
        
        # Generate comparison
        ai_engine = PMOAIEngine()
        comparison = ai_engine.compare_projects(projects_data)
        
        return Response(comparison)


class ExecutiveReportView(APIView):
    """
    Generate comprehensive executive report
    """
    def get(self, request):
        # Get portfolio data
        portfolio_data = {
            'total_projects': Project.objects.count(),
            'on_track': Project.objects.filter(status='on_track').count(),
            'at_risk': Project.objects.filter(status='at_risk').count(),
            'delayed': Project.objects.filter(status='delayed').count(),
            'avg_completion': round(Project.objects.aggregate(
                avg=Avg('completion_percentage')
            )['avg'] or 0, 2),
            'projects_behind_schedule': Project.objects.filter(spi__lt=0.9).count(),
            'total_risks': Risk.objects.count(),
            'high_risks': Risk.objects.filter(severity__in=['high', 'critical']).count(),
        }
        
        # Get top critical projects
        critical_projects = Project.objects.filter(
            status__in=['at_risk', 'delayed']
        )[:10]
        
        projects_data = []
        for project in critical_projects:
            projects_data.append({
                'name': project.name,
                'status': project.status,
                'spi': float(project.spi),
                'completion_percentage': project.completion_percentage,
                'health_score': project.health_score,
            })
        
        # Generate executive report
        ai_engine = PMOAIEngine()
        report = ai_engine.generate_executive_report(portfolio_data, projects_data)
        
        return Response(report)
