import json
from typing import Dict, List, Any, Optional
from decimal import Decimal
from django.conf import settings


def convert_decimals(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj


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

OUTPUT FORMATTING:
- Use simple bullet points (•) for lists
- Use numbered lists (1. 2. 3.) for sequential actions
- Use clear section headers (no emojis, no markdown bold)
- Keep paragraphs short (2-3 sentences max)
- Use proper spacing between sections
- Start with most important information first

RESPONSE STRUCTURE:
For any analysis, organize as:
1. Summary statement (1-2 lines)
2. Key findings (bullet points)
3. Details by category (if needed)
4. Recommendations (numbered list)

Example format:
"Portfolio Risk Level: Medium-High

Critical Findings:
• Finding 1
• Finding 2
• Finding 3

Immediate Actions Required:
1. Action item 1
2. Action item 2
3. Action item 3"

YOU CAN:
- Summarize project status
- Explain risks and root causes
- Generate executive summaries
- Answer PMO questions
- Compare projects
- Provide recommendations
- Identify trends and patterns

YOU CANNOT:
- Invent metrics
- Change KPI definitions
- Access external systems
- Make decisions for users
- Guarantee outcomes"""

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
            
            # Initialize client - handle different versions
            try:
                client = Anthropic(api_key=self.api_key)
            except TypeError as e:
                # Older version might not support certain parameters
                print(f"[AI] Anthropic client init warning: {e}")
                # Try alternative initialization
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=self.api_key)
                except:
                    # Fallback for very old versions
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
                # If not JSON, wrap it as a simple response
                return {
                    "response": response_text,
                    "raw_response": True
                }
        
        except Exception as e:
            print(f"[AI Error] {type(e).__name__}: {str(e)}")
            # Return structured error response
            return {
                "error": True,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "response": f"I encountered an error while processing your request. Please try again or rephrase your question.",
                "demo_fallback": self._get_demo_response(user_message)
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
        # Convert any Decimal objects to float
        context_data = convert_decimals(context_data)
        
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
        # Convert any Decimal objects to float
        projects_data = convert_decimals(projects_data)
        
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
        # Convert any Decimal objects to float
        portfolio_data = convert_decimals(portfolio_data)
        projects_data = convert_decimals(projects_data)
        
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