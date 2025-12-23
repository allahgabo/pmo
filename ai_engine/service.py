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
    Optimized for fast, actionable insights
    """
    
    # BALANCED SYSTEM PROMPT - Concise yet thorough
    SYSTEM_PROMPT = """You are an elite AI PMO Assistant specializing in project management, risk analysis, and strategic planning.

CORE PRINCIPLES:
• Provide focused, actionable insights with clear business impact
• Balance depth with clarity - be thorough but not verbose
• Quantify everything (%, $, days, risk scores)
• Every recommendation needs: action, owner, timeline, expected outcome

RESPONSE STRUCTURE:

Project Status:
- Executive Summary (2-3 sentences: health, key issue, critical action)
- Current State (metrics interpretation with business context)
- Root Cause Analysis (why it's happening)
- Impact Assessment (consequences with quantification)
- Recommendations (each with: action, owner, timeline, resources, success metric)
- Top 3-5 Immediate Actions

Portfolio Analysis:
- Health Overview (on-track/at-risk/critical breakdown)
- Critical Projects (top concerns with business impact)
- Pattern Analysis (common issues, success factors)
- Resource & Financial Performance
- Strategic Recommendations (5-7 with implementation details)
- Immediate Actions

Risk Analysis:
- Risk Profile (severity, probability, exposure calculation)
- Root Cause (2-3 levels deep)
- Impact Analysis (schedule, cost, strategic - best/likely/worst case)
- Mitigation Options (2-3 approaches with pros/cons)
- Contingency Plan
- Monitoring Approach (KPIs, thresholds, frequency)

FORMAT:
• Use markdown (## headers, • bullets, numbered lists)
• Lead with key insights, then support with detail
• Keep bullets focused - one clear point each
• Use tables for comparisons when helpful

QUALITY STANDARDS:
• Provide depth where it matters (root causes, implementation, risks)
• Skip obvious points - assume sophisticated audience
• Be specific: "reallocate 2 senior devs from Project A to B for 3 weeks" not "adjust resources"
• Include realistic timelines and resource needs
• Address "what could go wrong" proactively"""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = getattr(settings, 'AI_MODEL', 'claude-sonnet-4-20250514')
        # OPTIMIZED: 6000 tokens balances depth with speed
        self.max_tokens = getattr(settings, 'AI_MAX_TOKENS', 6000)
        self.demo_mode = self.api_key == 'demo-mode'
    
    def _validate_response(self, message) -> str:
        """Validate and extract text from Claude API response"""
        if not message or not hasattr(message, 'content'):
            raise ValueError("Invalid response structure from API")
        
        if not message.content or len(message.content) == 0:
            raise ValueError("Empty response from Claude API")
        
        return message.content[0].text
    
    def _call_claude_api(self, user_message: str, stream: bool = False) -> Dict[str, Any]:
        """
        Call Claude API with optional streaming support
        """
        if self.demo_mode:
            return self._get_demo_response(user_message)
        
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            if stream:
                # Streaming mode for better UX
                return {
                    "stream": True,
                    "stream_generator": client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        system=self.SYSTEM_PROMPT,
                        messages=[{"role": "user", "content": user_message}],
                        stream=True
                    )
                }
            else:
                # Standard mode
                message = client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=self.SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_message}]
                )
                
                response_text = self._validate_response(message)
                
                return {
                    "response": response_text,
                    "raw_response": True
                }
        
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            print(f"[AI Error] {error_type}: {error_msg}")
            
            return {
                "error": True,
                "error_type": error_type,
                "error_message": error_msg,
                "response": f"I encountered an error while processing your request: {error_msg}\n\nPlease try again or contact support if the issue persists."
            }
    
    def _get_demo_response(self, user_message: str) -> Dict[str, Any]:
        """Generate demo response based on request type"""
        return {
            "response": """This is a demo mode response. Enable the Anthropic API to get detailed AI analysis.

In production mode, I would provide:
• Comprehensive analysis with actionable insights
• Specific implementation plans with timelines
• Root cause investigations
• Risk mitigation strategies with success metrics

To enable full functionality, configure your Anthropic API key in settings.""",
            "demo_mode": True
        }
    
    def generate_project_summary(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI summary for a single project - OPTIMIZED"""
        project_data = convert_decimals(project_data)
        
        # BALANCED PROMPT - meaningful depth without verbosity
        prompt = f"""Analyze this project and provide focused, actionable insights.

PROJECT DATA:
{json.dumps(project_data, indent=2)}

Provide analysis covering:

## Executive Summary
Overall health, primary concern, and critical action needed (2-3 sentences).

## Current Status Analysis
• Interpret key metrics (completion %, SPI, CPI, budget, risks) in business terms
• How metrics relate and what story they tell
• Performance trajectory and concerns

## Root Cause Analysis
Why is the project performing this way? Identify 2-3 primary drivers with supporting evidence.

## Impact Assessment
• Consequences if unchanged (quantify delays, cost impact)
• Business and stakeholder implications
• Timeline sensitivity

## Recommendations
For each (provide 4-6):
1. Specific action to take
2. Owner (role/team)
3. Timeline (start/complete dates)
4. Expected outcome with metric
5. Resources needed
6. Key risks

## Top 3 High-Priority Risks
Brief analysis with mitigation approach for each.

## Immediate Actions (This Week)
Top 3-5 specific tasks with owners.

Target: Thorough but focused analysis (800-1200 words). Be specific and actionable."""
        
        return self._call_claude_api(prompt)
    
    def generate_portfolio_summary(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate portfolio-level executive summary - OPTIMIZED"""
        portfolio_data = convert_decimals(portfolio_data)
        
        prompt = f"""Provide executive portfolio analysis with strategic focus.

PORTFOLIO DATA:
{json.dumps(portfolio_data, indent=2)}

Provide:

## Executive Summary
Portfolio health, biggest risk, top recommendation, financial outlook (3-4 sentences).

## Portfolio Health Assessment
• On-track vs at-risk vs critical breakdown with business impact
• Completion trends and trajectory analysis
• Key health indicators and concerns

## Critical Projects (Top 3-5)
For each: current status, business impact if delayed, root cause, recommended intervention.

## Pattern Analysis
• Common issues across troubled projects
• Success factors in healthy projects
• Systemic problems requiring attention
• Process or capability gaps

## Resource & Financial Performance
• Resource utilization, constraints, and rebalancing needs
• Budget performance across portfolio
• Cost trends and financial risk exposure
• Value delivery assessment

## Strategic Recommendations (5-7)
Each with:
- Action and business justification
- Implementation approach with timeline
- Expected benefit (quantified)
- Resource requirements
- Key risks

## Immediate Actions (Next 2 Weeks)
Critical decisions, interventions, and resource moves needed.

Target: Strategic yet detailed analysis (1000-1500 words)."""
        
        return self._call_claude_api(prompt)
    
    def analyze_risk(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep risk analysis - OPTIMIZED"""
        risk_data = convert_decimals(risk_data)
        
        prompt = f"""Provide thorough risk analysis for decision-making.

RISK DATA:
{json.dumps(risk_data, indent=2)}

Provide:

## Risk Profile
• Severity level with justification
• Probability assessment (with confidence level)
• Risk exposure calculation (probability × impact)
• Urgency timeline

## Root Cause Analysis
Why does this risk exist? Go 2-3 levels deep to identify underlying factors.

## Impact Analysis
For each dimension (schedule, cost, quality, strategic):
- Quantified impact
- Affected stakeholders/projects
- Best case / Likely case / Worst case scenarios

## Mitigation Strategy
Provide 2-3 mitigation options:

**Option A (Aggressive):**
- Specific actions, resources, cost, timeline
- Expected risk reduction
- Implementation risks

**Option B (Moderate):**
- [same structure]

**Recommended approach with rationale**

## Contingency Plan
If risk materializes:
- Immediate response actions (first 48 hours)
- Key stakeholders and RACI
- Resources to have ready
- Decision triggers for escalation

## Monitoring & Early Warning
- Specific KPIs to track (with alert thresholds)
- Monitoring frequency and owner
- Early warning indicators

## Immediate Actions (48-72 Hours)
Top 3-5 urgent steps with owners and expected outcomes.

Target: Decision-ready analysis (700-1100 words)."""
        
        return self._call_claude_api(prompt)
    
    def answer_pmo_question(self, question: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Answer PMO questions - OPTIMIZED"""
        context_data = convert_decimals(context_data)
        
        prompt = f"""Answer this PMO question with thorough, actionable analysis.

QUESTION: "{question}"

CONTEXT DATA:
{json.dumps(context_data, indent=2)}

Provide:

## Direct Answer
Executive summary directly addressing the question (2-3 sentences).

## Detailed Analysis
• Current state assessment from provided data
• Root causes and contributing factors (with supporting evidence)
• Business impact and implications
• Multi-perspective view (technical, process, people, strategic)
• Relevant patterns or trends in the data

## Recommendations

**Immediate Actions (This Week):**
For each: specific steps, owner, resources, timeline, expected outcome

**Short-term Actions (Next 4 Weeks):**
[same structure]

**Long-term Strategic Actions:**
[same structure]

## Implementation Guidance
• How to execute recommendations effectively
• Potential obstacles with solutions
• Stakeholder communication needs
• Change management considerations

## Risk Assessment
• What could go wrong with recommended approach
• Mitigation strategies for each risk
• Contingency options (Plan B)

## Success Metrics
• How to measure if recommendations are working
• KPIs to track (with targets and timeframes)
• Review points and adjustment triggers

## Alternative Approaches
Brief analysis of 1-2 alternative solutions with pros/cons.

Target: Comprehensive yet focused (900-1400 words)."""
        
        return self._call_claude_api(prompt)
    
    def compare_projects(self, projects_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comparative project analysis - OPTIMIZED"""
        projects_data = convert_decimals(projects_data)
        
        prompt = f"""Compare these projects and provide strategic portfolio insights.

PROJECTS DATA:
{json.dumps(projects_data, indent=2)}

Provide:

## Performance Overview
• Projects ranked by overall health with rationale
• Key metrics comparison (table format if multiple metrics)
• Best performers: what makes them successful
• Worst performers: root causes of struggles

## Pattern Analysis
• Common success factors across healthy projects
• Common failure modes in struggling projects
• Process, resource, leadership, and technical patterns
• Systemic issues affecting multiple projects

## Metric Analysis
Compare performance across:
- Schedule (SPI comparison with insights)
- Cost (CPI and budget utilization)
- Risk profiles
- Resource allocation effectiveness

Identify outliers and explain significance.

## Resource & Financial Analysis
• Resource efficiency by project
• Over/under-resourced projects
• Budget performance and ROI comparison
• Optimal allocation recommendations

## Strategic Insights
• Which projects drive most strategic value
• Portfolio balance assessment
• Investment allocation optimization
• Alignment with organizational goals

## Project-Specific Recommendations
For each at-risk project:
- Key actions to improve performance
- Resource adjustments needed
- Timeline for improvement
- Success metrics

## Portfolio-Level Recommendations (5-7)
• Resource rebalancing strategy
• Projects to accelerate/defer/cancel with rationale
• Process improvements across portfolio
• Capability building priorities
• Governance changes

## Lessons & Best Practices
• What to replicate from successful projects
• What to avoid from struggling projects
• Knowledge transfer opportunities

## Immediate Actions (Next 2 Weeks)
Critical interventions, resource moves, decisions required.

Target: Strategic comparative analysis (1200-1800 words)."""
        
        return self._call_claude_api(prompt)
    
    def generate_executive_report(self, portfolio_data: Dict[str, Any], 
                                 projects_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate C-level executive report - OPTIMIZED"""
        portfolio_data = convert_decimals(portfolio_data)
        projects_data = convert_decimals(projects_data)
        
        prompt = f"""Generate executive PMO report for C-level/board presentation.

PORTFOLIO DATA:
{json.dumps(portfolio_data, indent=2)}

KEY PROJECTS:
{json.dumps(projects_data, indent=2)}

Provide:

## Executive Summary
• Portfolio health in business terms
• Top 3 achievements and top 3 concerns
• Critical decision needed
• Financial outlook and strategic alignment status

## Portfolio Performance Dashboard
• Key metrics with trends (vs. targets, YoY/QoQ changes)
• Health score breakdown by project category
• Performance trajectory

## Strategic Alignment
• How portfolio delivers on company strategy
• Value delivery vs. investment analysis
• Strategic gaps, overinvestments, or balance issues
• Realignment recommendations

## Critical Projects Deep Dive (Top 3-5)
For each:
- Current status and trajectory
- Business impact if delayed/failed
- Root causes of issues
- Recommended interventions with timeline
- Resource needs and executive decisions required

## Financial Performance
• Budget vs. actual across portfolio
• Cost overrun drivers and trends
• Forecasted costs to completion
• ROI analysis by project category
• Financial risk exposure

## Top 10 Portfolio Risks
Brief analysis of highest risks with:
- Risk exposure quantification
- Systemic risks affecting multiple projects
- Mitigation status
- Risks requiring executive attention

## Resource Analysis
• Current utilization and critical constraints
• Skills gap analysis
• Rebalancing opportunities
• Strategic hiring/contracting needs
• Organizational capacity assessment

## Strategic Recommendations for Leadership (7-10)
Each covering portfolio prioritization, resource strategy, process improvements, capability building:
- Business rationale with quantified benefits
- Implementation approach and timeline
- Resource requirements
- Success metrics
- Key risks and dependencies

## Critical Decisions Required
For each decision:
- Options with pros/cons
- Recommendation with rationale
- Decision timeline
- Impact of delay

## Next 30 Days - Immediate Actions
• Top priorities by stakeholder
• Quick wins
• Critical interventions
• Resource actions

## 3-6 Month Outlook
• Portfolio trajectory and major milestones
• Anticipated challenges and opportunities
• Investment needs and organizational readiness

Target: Presentation-ready executive report (1800-2500 words)."""
        
        return self._call_claude_api(prompt)