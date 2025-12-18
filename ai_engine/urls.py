from django.urls import path
from .views import (
    ProjectSummaryView,
    PortfolioSummaryView,
    RiskAnalysisView,
    PMOQuestionView,
    ProjectComparisonView,
    ExecutiveReportView,
)

urlpatterns = [
    path('project-summary/<int:project_id>/', ProjectSummaryView.as_view(), name='project-summary'),
    path('portfolio-summary/', PortfolioSummaryView.as_view(), name='portfolio-summary'),
    path('risk-analysis/<int:risk_id>/', RiskAnalysisView.as_view(), name='risk-analysis'),
    path('ask/', PMOQuestionView.as_view(), name='pmo-question'),
    path('compare-projects/', ProjectComparisonView.as_view(), name='compare-projects'),
    path('executive-report/', ExecutiveReportView.as_view(), name='executive-report'),
]
