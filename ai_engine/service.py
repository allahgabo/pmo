import json
from typing import Dict, List, Any, Optional
from django.conf import settings


class PMOAIEngine:
    """
    AI Engine for PMO analysis using Claude API
    Generates insights, summaries, and recommendations based on project data
    """
    
    SYSTEM_PROMPT = """You are an enterprise-grade AI Project Management Office (PMO) Assistant.
Your mission is to help PMO teams, Project Managers, and Executives
understand project and portfolio health, risks, performance, and actions
based ONLY on the data provided to you.

GENERAL RULES:
- Use clear, business-friendly language
- Be concise, executive-ready, and decision-oriented
- Avoid technical jargon unless explicitly requested
- Never hallucinate or assume missing data
- If data is insufficient, state it clearly
- Always explain WHY, not just WHAT
- Prioritize impact and recommended actions

OUTPUT RULES:
- Always return VALID JSON
- Do not include any text outside JSON
- Use null if a value is unavailable
- Use arrays for lists
- Use short, clear sentences

YOU CAN:
- Summarize project status
- Explain risks and root causes
- Generate executive summaries
- Answer PMO questions
- Compare projects
- Provide recommendations

YOU CANNOT:
- Invent metrics
- Change KPI definitions
- Access external systems"""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.demo_mode = self.api_key == 'demo-mode'
    
    def _call_claude_api(self, user_message: str) -> Dict[str, Any]:
        """
        Call Claude API (or return demo response in demo mode)
        """
        if self.demo_mode:
            return self._get_demo_response(user_message)
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            response_text = message.content[0].text
            
            # Try to parse as JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If not JSON, wrap it
                return {
                    "response": response_text,
                    "raw_response": True
                }
        
        except Exception as e:
            return {
                "error": str(e),
                "demo_mode": True,
                "message": "Error calling AI API, returning demo response"
            }
    
    def _get_demo_response(self, user_message: str) -> Dict[str, Any]:
        """Generate demo response based on request type"""
        if "status summary" in user_message.lower():
            return {
                "context": {
                    "level": "project",
                    "report_type": "status_summary"
                },
                "health_summary": {
                    "status": "At Risk",
                    "overall_assessment": "The project is behind schedule with multiple high-impact risks affecting delivery."
                },
                "insights": [
                    "Schedule performance is the primary driver of project risk.",
                    "Risk exposure is increasing as completion remains below expected levels."
                ],
                "recommendations": [
                    "Rebaseline critical tasks and apply recovery planning.",
                    "Escalate high risks to the steering committee.",
                    "Consider adding resources to critical path activities."
                ],
                "data_gaps": []
            }
        
        elif "portfolio" in user_message.lower():
            return {
                "context": {
                    "level": "portfolio",
                    "report_type": "executive_summary"
                },
                "health_summary": {
                    "status": "Mixed",
                    "overall_assessment": "Portfolio shows healthy completion rates but resource constraints are emerging."
                },
                "insights": [
                    "55% of projects are on track, indicating good overall portfolio health.",
                    "Developer and QA roles are overallocated across multiple projects.",
                    "7 projects with SPI < 0.9 require immediate attention."
                ],
                "recommendations": [
                    "Prioritize resource allocation for critical projects.",
                    "Consider hiring additional developers and QA engineers.",
                    "Implement stricter schedule monitoring for at-risk projects."
                ],
                "data_gaps": []
            }
        
        else:
            return {
                "response": "I can help you analyze project data. Please provide specific project information or ask about portfolio status.",
                "capabilities": [
                    "Project status summaries",
                    "Risk analysis",
                    "Portfolio health reports",
                    "Performance insights",
                    "Recommendations"
                ]
            }
    
    def generate_project_summary(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI summary for a single project
        """
        prompt = f"""Generate a project status summary using the following data:

Project Name: {project_data.get('name')}
Status: {project_data.get('status')}
Completion Percentage: {project_data.get('completion_percentage')}
SPI: {project_data.get('spi')}
CPI: {project_data.get('cpi')}
Total Risks: {project_data.get('total_risks')}
High Risks: {project_data.get('high_risks')}
Budget: {project_data.get('budget')}
Spent: {project_data.get('spent')}
Days Remaining: {project_data.get('days_remaining')}

Return a JSON response with: context, health_summary, key_metrics, risk_analysis, insights, recommendations, data_gaps"""
        
        return self._call_claude_api(prompt)
    
    def generate_portfolio_summary(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI summary for the entire portfolio
        """
        prompt = f"""Generate a portfolio-level executive summary.

Total Projects: {portfolio_data.get('total_projects')}
On Track: {portfolio_data.get('on_track')}
At Risk: {portfolio_data.get('at_risk')}
Delayed: {portfolio_data.get('delayed')}
Projects with SPI < 0.9: {portfolio_data.get('projects_behind_schedule')}
Average Completion: {portfolio_data.get('avg_completion')}%
Total Risks: {portfolio_data.get('total_risks')}
High Priority Risks: {portfolio_data.get('high_risks')}

Return a JSON response with: context, health_summary, key_metrics, insights, recommendations, data_gaps"""
        
        return self._call_claude_api(prompt)
    
    def analyze_risk(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a specific risk and provide recommendations
        """
        prompt = f"""Analyze this project risk:

Risk Title: {risk_data.get('title')}
Category: {risk_data.get('category')}
Severity: {risk_data.get('severity')}
Probability: {risk_data.get('probability')}%
Impact: {risk_data.get('impact')}/10
Description: {risk_data.get('description')}
Current Mitigation: {risk_data.get('mitigation_plan')}

Provide detailed risk analysis including:
- Root cause analysis
- Business impact assessment
- Recommended mitigation strategies
- Monitoring approach

Return a JSON response."""
        
        return self._call_claude_api(prompt)
    
    def answer_pmo_question(self, question: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer a specific PMO question using provided context
        """
        prompt = f"""Answer the PMO question below using the provided data.

User Question: "{question}"

Context Data:
{json.dumps(context_data, indent=2)}

Provide a clear, actionable answer. Return a JSON response."""
        
        return self._call_claude_api(prompt)
    
    def compare_projects(self, projects_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple projects and identify patterns
        """
        prompt = f"""Compare the following projects and identify patterns, risks, and recommendations:

{json.dumps(projects_data, indent=2)}

Analyze:
- Performance trends
- Common risk patterns
- Resource allocation efficiency
- Recommendations for improvement

Return a JSON response."""
        
        return self._call_claude_api(prompt)
    
    def generate_executive_report(self, portfolio_data: Dict[str, Any], 
                                 projects_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive executive report
        """
        prompt = f"""Generate an executive-level PMO report.

Portfolio Overview:
{json.dumps(portfolio_data, indent=2)}

Key Projects:
{json.dumps(projects_data, indent=2)}

Provide:
- Executive summary
- Key performance indicators
- Critical issues and risks
- Strategic recommendations
- Action items

Return a JSON response suitable for C-level presentation."""
        
        return self._call_claude_api(prompt)
