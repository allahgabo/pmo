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
        projects = Project.objects.all()[:5]
        recent_projects = []
        for p in projects:
            recent_projects.append({
                'name': p.name,
                'code': p.code,
                'status': p.status,
                'spi': float(p.spi),
                'cpi': float(p.cpi),
                'completion_percentage': p.completion_percentage,
                'health_score': p.health_score,
            })
        
        context_data = {
            'portfolio': {
                'total_projects': Project.objects.count(),
                'on_track': Project.objects.filter(status='on_track').count(),
                'at_risk': Project.objects.filter(status='at_risk').count(),
                'delayed': Project.objects.filter(status='delayed').count(),
            },
            'recent_projects': recent_projects
        }
        
        # Get AI answer
        ai_engine = PMOAIEngine()
        ai_response = ai_engine.answer_pmo_question(question, context_data)
        
        # Format response for frontend
        # AI might return structured JSON or a simple response
        if isinstance(ai_response, dict):
            if 'response' in ai_response:
                # Simple response format - convert newlines to HTML
                raw_text = ai_response['response']
                
                # Check if raw_text itself is a JSON string
                import json
                try:
                    parsed = json.loads(raw_text)
                    if isinstance(parsed, dict) and 'response' in parsed:
                        raw_text = parsed['response']
                except (json.JSONDecodeError, TypeError):
                    pass
                
                # Strip JSON wrapper if present
                import re
                raw_text = re.sub(r'^```json\s*\n?', '', raw_text, flags=re.IGNORECASE)
                raw_text = re.sub(r'\n?```\s*$', '', raw_text)
                raw_text = re.sub(r'^\{\s*"response":\s*"', '', raw_text)
                raw_text = re.sub(r'"\s*\}\s*$', '', raw_text)
                
                # Now convert newlines to <br>
                answer_text = raw_text.replace('\\n', '<br>').replace('\n', '<br>')
            elif 'answer' in ai_response:
                # Already has answer key - convert newlines to HTML
                answer_text = ai_response['answer'].replace('\\n', '<br>').replace('\n', '<br>')
            else:
                # Convert structured response to HTML
                answer_text = self._format_ai_response(ai_response)
        else:
            raw_text = str(ai_response)
            # Strip JSON wrapper if present
            import re
            raw_text = re.sub(r'^```json\s*\n?', '', raw_text, flags=re.IGNORECASE)
            raw_text = re.sub(r'\n?```\s*$', '', raw_text)
            answer_text = raw_text.replace('\\n', '<br>').replace('\n', '<br>')
        
        return Response({
            'answer': answer_text,
            'full_response': ai_response,
            'is_html': True  # Flag to tell frontend this is HTML
        })
    
    def _format_ai_response(self, ai_response):
        """Format structured AI response into HTML with proper line breaks"""
        import json
        parts = []
        
        # Handle new JSON structure with summary, critical_risks, etc.
        if 'summary' in ai_response:
            parts.append(f"<strong>Summary:</strong><br>")
            parts.append(f"{ai_response['summary']}<br><br>")
        
        if 'critical_risks' in ai_response and ai_response['critical_risks']:
            parts.append(f"<strong>Critical Risks:</strong><br>")
            for risk in ai_response['critical_risks']:
                parts.append(f"• {risk}<br>")
            parts.append("<br>")
        
        if 'risk_indicators' in ai_response and ai_response['risk_indicators']:
            parts.append(f"<strong>Risk Indicators:</strong><br>")
            for indicator in ai_response['risk_indicators']:
                parts.append(f"• {indicator}<br>")
            parts.append("<br>")
        
        if 'risk_categories' in ai_response and ai_response['risk_categories']:
            categories = ai_response['risk_categories']
            
            if 'high_risk' in categories and categories['high_risk']:
                parts.append(f"<strong>High Risk Projects:</strong><br>")
                for item in categories['high_risk']:
                    parts.append(f"<strong>{item.get('project', 'Unknown')}</strong><br>")
                    if 'risks' in item:
                        for risk in item['risks']:
                            parts.append(f"&nbsp;&nbsp;&nbsp;• {risk}<br>")
                parts.append("<br>")
            
            if 'medium_risk' in categories and categories['medium_risk']:
                parts.append(f"<strong>Medium Risk Projects:</strong><br>")
                for item in categories['medium_risk']:
                    parts.append(f"<strong>{item.get('project', 'Unknown')}</strong><br>")
                    if 'risks' in item:
                        for risk in item['risks']:
                            parts.append(f"&nbsp;&nbsp;&nbsp;• {risk}<br>")
                parts.append("<br>")
        
        if 'immediate_actions' in ai_response and ai_response['immediate_actions']:
            parts.append(f"<strong>Immediate Actions Required:</strong><br>")
            for i, action in enumerate(ai_response['immediate_actions'], 1):
                parts.append(f"{i}. {action}<br>")
            parts.append("<br>")
        
        if 'monitoring_focus' in ai_response and ai_response['monitoring_focus']:
            parts.append(f"<strong>Monitoring Focus:</strong><br>")
            for focus in ai_response['monitoring_focus']:
                parts.append(f"• {focus}<br>")
            parts.append("<br>")
        
        # Handle risk_assessment structure
        if 'risk_assessment' in ai_response:
            risk = ai_response['risk_assessment']
            
            if 'portfolio_risk_level' in risk:
                parts.append(f"<strong>Portfolio Risk Level: {risk['portfolio_risk_level']}</strong><br><br>")
            
            if 'critical_findings' in risk and risk['critical_findings']:
                parts.append("<strong>Critical Findings:</strong><br>")
                for finding in risk['critical_findings']:
                    parts.append(f"• {finding}<br>")
                parts.append("<br>")
        
        # Handle identified_risks
        if 'identified_risks' in ai_response and ai_response['identified_risks']:
            parts.append("<strong>Projects Requiring Immediate Attention:</strong><br><br>")
            
            for i, risk in enumerate(ai_response['identified_risks'], 1):
                parts.append(f"<strong>{i}. {risk.get('project', 'Unknown Project')} - {risk.get('risk_level', 'Unknown')} Risk</strong><br>")
                
                if 'key_risks' in risk and risk['key_risks']:
                    for key_risk in risk['key_risks']:
                        parts.append(f"&nbsp;&nbsp;&nbsp;• {key_risk}<br>")
                
                if 'impact' in risk:
                    parts.append(f"&nbsp;&nbsp;&nbsp;Impact: {risk['impact']}<br>")
                
                parts.append("<br>")
        
        # Handle portfolio_risk_indicators
        if 'portfolio_risk_indicators' in ai_response and ai_response['portfolio_risk_indicators']:
            parts.append("<strong>Portfolio Risk Indicators:</strong><br><br>")
            
            for indicator in ai_response['portfolio_risk_indicators']:
                parts.append(f"• <strong>{indicator.get('indicator', 'Indicator')}:</strong> {indicator.get('status', 'Unknown')}<br>")
                if 'details' in indicator:
                    parts.append(f"&nbsp;&nbsp;{indicator['details']}<br>")
            parts.append("<br>")
        
        # Handle recommended_risk_controls
        if 'recommended_risk_controls' in ai_response and ai_response['recommended_risk_controls']:
            parts.append("<strong>Recommended Risk Controls:</strong><br><br>")
            for i, control in enumerate(ai_response['recommended_risk_controls'], 1):
                parts.append(f"{i}. {control}<br>")
            parts.append("<br>")
        
        # Handle health_summary (legacy format)
        if 'health_summary' in ai_response and not parts:
            summary = ai_response['health_summary']
            if isinstance(summary, dict):
                if 'status' in summary:
                    parts.append(f"<strong>Status: {summary.get('status')}</strong><br>")
                if 'overall_assessment' in summary:
                    parts.append(f"{summary.get('overall_assessment')}<br><br>")
        
        # Handle insights (legacy format)
        if 'insights' in ai_response and ai_response['insights'] and not any('Insights' in p for p in parts):
            parts.append("<strong>Key Insights:</strong><br>")
            for insight in ai_response['insights']:
                parts.append(f"• {insight}<br>")
            parts.append("<br>")
        
        # Handle recommendations (legacy format)
        if 'recommendations' in ai_response and ai_response['recommendations'] and not any('Recommendations' in p for p in parts):
            parts.append("<strong>Recommendations:</strong><br>")
            for i, rec in enumerate(ai_response['recommendations'], 1):
                parts.append(f"{i}. {rec}<br>")
            parts.append("<br>")
        
        # Handle key_metrics
        if 'key_metrics' in ai_response and ai_response['key_metrics']:
            parts.append("<strong>Key Metrics:</strong><br>")
            metrics = ai_response['key_metrics']
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    parts.append(f"• {key}: {value}<br>")
            parts.append("<br>")
        
        # If we have content, return it
        if parts:
            return "".join(parts)
        
        # Fallback: Format the text with line breaks
        if isinstance(ai_response, str):
            return ai_response.replace('\n', '<br>')
        
        # Last resort: Pretty print JSON
        return "<pre>" + json.dumps(ai_response, indent=2) + "</pre>"


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